import os
import time
import requests
import feedparser
import threading
import datetime
import re
from bs4 import BeautifulSoup
from database import get_connection
import cloudscraper
from dotenv import load_dotenv
from google import genai
from unicodedata import normalize
from collections import Counter

load_dotenv()

# ==================== CONFIGURAÇÃO GEMINI ====================
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai_client = genai.Client(api_key=GEMINI_API_KEY)
    MODELOS_GEMINI = [
        'gemini-3.1-flash-lite',
        'gemini-3.5-flash',
        'gemini-3-flash',
        'gemini-2.5-flash-lite',
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-3.1-pro',
        'gemini-2-flash',
        'gemini-2-flash-lite'
    ]
else:
    genai_client = None
    MODELOS_GEMINI = []
    print("⚠️ GEMINI_API_KEY não encontrada. Resumos IA desabilitados.")

def resumir_com_gemini(titulo, corpo, max_caracteres=150):
    """Gera resumo curto com fallback automático entre TODOS os modelos."""
    if not genai_client or not corpo or len(corpo) < 50:
        return None

    prompt = f"""Você é um redator de resumos para um portal de notícias.
Gere um resumo curto (máximo {max_caracteres} caracteres) da notícia abaixo.

REGRAS:
1. NÃO repita o título.
2. Adicione uma informação EXTRA que não esteja no título (ex: números, causas, consequências, local detalhado, declarações).
3. Seja direto, em português, sem frases introdutórias.
4. Responda APENAS com o resumo.

TÍTULO: {titulo}

NOTÍCIA: {corpo[:3000]}

RESUMO:"""

    for modelo in MODELOS_GEMINI:
        try:
            response = genai_client.models.generate_content(
                model=modelo,
                contents=prompt
            )
            if response.text:
                resumo = response.text.strip()
                resumo = re.sub(r'^["\']|["\']$', '', resumo)
                if len(resumo) > max_caracteres:
                    corte = resumo[:max_caracteres]
                    ultimo_espaco = corte.rfind(' ')
                    if ultimo_espaco > 0:
                        resumo = corte[:ultimo_espaco] + '...'
                    else:
                        resumo = corte + '...'
                return resumo
            # Resposta vazia -> próximo modelo
            continue
        except Exception as e:
            erro_str = str(e)
            # Se modelo não existe (404) ou quota esgotada (429), pula sem log excessivo
            if '404' in erro_str or '429' in erro_str or 'RESOURCE_EXHAUSTED' in erro_str:
                # Log apenas para modelos com cota, para não poluir
                if modelo in ['gemini-3.1-flash-lite', 'gemini-3.5-flash', 'gemini-3-flash', 'gemini-2.5-flash-lite', 'gemini-2.5-flash']:
                    print(f"Modelo {modelo} indisponível (quota/404)")
                continue
            # Outros erros: log e continua
            print(f"Erro com modelo {modelo}: {erro_str[:200]}")
            continue

    # Se todos falharem
    print(f"Todos os modelos falharam para: {titulo[:150]}...")
    return None

# ==================== FUNÇÕES AUXILIARES ====================
def classificar_categoria(texto):
    """
    Classifica a categoria de uma notícia com base na contagem de palavras-chave.
    Remove acentos, normaliza o texto e conta ocorrências de cada categoria.
    Retorna a categoria com maior pontuação ou 'Geral' se nenhuma palavra for encontrada.
    """
    # 1. Normalização: remove acentos e converte para minúsculas
    texto_limpo = normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').lower()
    
    # 2. Dicionário de categorias e suas palavras-chave (já sem acentos)
    categorias = {
        'Clima': ['alagamento', 'chuva', 'granizo', 'temporal', 'clima', 'estragos', 'deslizamento', 'enchente'],
        'Segurança Pública': ['policia', 'preso', 'roubo', 'bombeiros', 'furto', 'crime', 'investigacao', 'homicidio', 'assassinato', 'trafico', 'drogas'],
        'Esporte': ['futebol', 'campeonato', 'torneio', 'atleta', 'esporte', 'copa', 'medalha', 'olimpiadas', 'brasileirao'],
        'Cidadania': ['prefeitura', 'camara', 'vereadores', 'imposto', 'obras', 'licitacao', 'prefeito', 'governo', 'iptu', 'politica'],
        'Saúde': ['saude', 'hospital', 'medico', 'dengue', 'vacina', 'ubs', 'paciente', 'remedio', 'campanha', 'doenca', 'virus', 'leishmaniose'],
        'Educação': ['educacao', 'escola', 'aluno', 'professor', 'ensino', 'faculdade', 'creche', 'universidade', 'unesp', 'fatec', 'etec'],
        'Eventos': ['festa', 'show', 'evento', 'festival', 'ingresso', 'exposicao', 'musica'],
        'Agronegócio': ['agronegocio', 'safra', 'soja', 'rural', 'colheita', 'gado', 'plantio', 'fazenda', 'agricultura'],
        'Negócios': ['empreendedorismo', 'tecnologia', 'inovacao', 'startup', 'negocios', 'economia', 'financas', 'investimento', 'mercado'],
        'Cultura': ['cultura', 'tradicao', 'folclore', 'historia', 'patrimonio', 'turismo', 'gastronomia'],
        'Trânsito': ['colisao', 'transito', 'acidente', 'rodovia', 'estrada', 'congestionamento', 'viagem', 'transporte'],
        'Meio Ambiente': ['ambiente', 'sustentabilidade', 'reciclagem', 'poluicao', 'desmatamento', 'conservacao'],
        'Cotidiano': ['cotidiano', 'comportamento', 'lifestyle', 'moda', 'culinaria', 'hobby', 'viagem'],
        'Ciência e Tecnologia': ['ciencia', 'pesquisa', 'tecnologia', 'inovacao', 'universidade', 'descoberta', 'espaco']
    }
    
    # 3. Frases compostas (verificação separada, pois são duas ou mais palavras)
    frases_compostas = {
        'Meio Ambiente': ['meio ambiente', 'defesa civil'],
        'Saúde': ['saude mental']
    }
    
    # 4. Contagem de palavras por categoria
    contagem = {}
    for cat, palavras in categorias.items():
        total = sum(len(re.findall(rf'\b{re.escape(palavra)}\b', texto_limpo)) for palavra in palavras)
        if total > 0:
            contagem[cat] = total
    
    # 5. Adicionar contagem de frases compostas
    for cat, lista_frases in frases_compostas.items():
        for frase in lista_frases:
            if frase in texto_limpo:
                contagem[cat] = contagem.get(cat, 0) + 1
    
    # 6. Se nenhuma palavra foi encontrada, retorna 'Geral'
    if not contagem:
        return 'Geral'
    
    # 7. Retorna a categoria com maior contagem (em caso de empate, a primeira encontrada)
    return max(contagem, key=contagem.get)

def extrair_cidade(titulo, corpo, cidades_lista):
    texto_titulo = titulo.lower()
    encontradas_titulo = {c for c in cidades_lista if re.search(fr'\b{re.escape(c.lower())}\b', texto_titulo)}
    if len(encontradas_titulo) == 1:
        return list(encontradas_titulo)[0]
    texto_completo = f"{texto_titulo} {corpo.lower() if corpo else ''}"
    encontradas_texto = {c for c in cidades_lista if re.search(fr'\b{re.escape(c.lower())}\b', texto_completo)}
    if len(encontradas_texto) == 1:
        return list(encontradas_texto)[0]
    elif len(encontradas_texto) > 1:
        return 'Região Alta Paulista'
    return 'Outras Regiões'

def formatar_data_html(soup):
    meta_pub = soup.find('meta', property='article:published_time') or soup.find('meta', attrs={'itemprop': 'datePublished'})
    if meta_pub and meta_pub.get('content'):
        try:
            return re.sub(r'T', ' ', meta_pub['content'][:19])
        except:
            pass
    return None

def buscar_corpo_noticia(url, scraper):
    try:
        response = scraper.get(url, timeout=15)
        if response.status_code != 200:
            return "", None, ""
        soup = BeautifulSoup(response.text, 'html.parser')
        data_encontrada = formatar_data_html(soup)
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', property='og:description')
        resumo_oficial = meta_desc['content'] if meta_desc and meta_desc.get('content') else ""
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
            tag.decompose()
        article = soup.find('article') or soup.find('main')
        if not article:
            article = soup.find('div', class_=re.compile(r'content|post|text|materia|noticia', re.I))
        if not article:
            article = soup.body
        corpo_texto = ""
        if article:
            if 'g1.globo.com' in url:
                content_div = soup.find('div', class_='content-text') or \
                              soup.find('div', class_=re.compile(r'mc-column|body-text', re.I))
                if content_div:
                    article = content_div
            paragrafos = article.find_all('p')
            if paragrafos:
                corpo_texto = ' '.join(p.get_text(separator=' ', strip=True) for p in paragrafos)
            else:
                corpo_texto = article.get_text(separator=' ', strip=True)
            corpo_texto = re.sub(r'\s+', ' ', corpo_texto).strip()
        if len(corpo_texto) < 100 and resumo_oficial:
            corpo_texto = resumo_oficial
        return corpo_texto, data_encontrada, resumo_oficial
    except Exception as e:
        print(f"Erro ao buscar corpo: {e}")
        return "", None, ""

# ==================== PROCESSADORES ====================
def processar_html(fonte, cidades_lista, cursor, db, scraper):
    try:
        response = scraper.get(fonte['url'], timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        cabecalhos = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        noticias_salvas = 0
        for elemento in cabecalhos:
            if noticias_salvas >= 10:
                break
            link_tag = elemento.find('a') if elemento.find('a') else (elemento if elemento.name == 'a' else None)
            if not link_tag:
                continue
            titulo = link_tag.get_text(strip=True)
            if len(titulo) > 25:
                link = link_tag.get('href')
                if not link:
                    continue
                if not link.startswith('http'):
                    dominio_base = '/'.join(fonte['url'].split('/')[:3])
                    link = dominio_base + '/' + link.lstrip('/')
                corpo_completo, data_html, _ = buscar_corpo_noticia(link, scraper)
                cidade_mencionada = extrair_cidade(titulo, corpo_completo, cidades_lista)
                categoria = classificar_categoria(f"{titulo} {corpo_completo}")
                resumo_ia = resumir_com_gemini(titulo, corpo_completo)
                if not resumo_ia and corpo_completo:
                    resumo_ia = corpo_completo[:150] + '...' if len(corpo_completo) > 150 else corpo_completo
                elif not resumo_ia:
                    resumo_ia = "Acesse para ler na íntegra."
                data_publicacao = data_html if data_html else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data_importacao = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                try:
                    sql = """INSERT IGNORE INTO noticias 
                             (fonte_id, cidade_mencionada, titulo, resumo, corpo_completo, url_original, categoria, data_publicacao, data_importacao) 
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (fonte['id'], cidade_mencionada, titulo, resumo_ia, corpo_completo, link, categoria, data_publicacao, data_importacao))
                    db.commit()
                    noticias_salvas += 1
                    time.sleep(0.5)  # Delay para não sobrecarregar API
                except Exception:
                    pass
    except Exception as e:
        print(f"Erro no processamento HTML da fonte {fonte.get('id')}: {e}")

def processar_rss(fonte, cidades_lista, cursor, db, scraper):
    try:
        feed = feedparser.parse(fonte['url'])
        noticias_salvas = 0
        for entry in feed.entries:
            if noticias_salvas >= 10:
                break
            titulo = entry.title
            link = entry.link
            corpo_completo, data_html, resumo_html = buscar_corpo_noticia(link, scraper)
            if not corpo_completo or len(corpo_completo) < 50:
                desc_bruta = entry.get('description', '')
                if desc_bruta:
                    soup_desc = BeautifulSoup(desc_bruta, 'html.parser')
                    corpo_completo = soup_desc.get_text(separator=' ', strip=True)
            cidade_mencionada = extrair_cidade(titulo, corpo_completo, cidades_lista)
            categoria = classificar_categoria(f"{titulo} {corpo_completo}")
            resumo_ia = resumir_com_gemini(titulo, corpo_completo)
            if not resumo_ia and corpo_completo:
                resumo_ia = corpo_completo[:150] + '...' if len(corpo_completo) > 150 else corpo_completo
            elif not resumo_ia:
                resumo_ia = "Acesse para ler na íntegra."
            data_publicacao = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if 'published_parsed' in entry and entry.published_parsed:
                try:
                    data_publicacao = time.strftime('%Y-%m-%d %H:%M:%S', entry.published_parsed)
                except:
                    pass
            data_importacao = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                sql = """INSERT IGNORE INTO noticias 
                         (fonte_id, cidade_mencionada, titulo, resumo, corpo_completo, url_original, categoria, data_publicacao, data_importacao) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(sql, (fonte['id'], cidade_mencionada, titulo, resumo_ia, corpo_completo, link, categoria, data_publicacao, data_importacao))
                db.commit()
                noticias_salvas += 1
                time.sleep(0.5)
            except Exception:
                pass
    except Exception as e:
        print(f"Erro no processamento RSS da fonte {fonte.get('id')}: {e}")

# ==================== VARREDURA PRINCIPAL ====================
def varredura_inteligente():
    print(f"[{datetime.datetime.now()}] Iniciando varredura com IA integrada...")
    db = get_connection()
    if not db:
        print("Erro: Não foi possível conectar ao banco.")
        return
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT nome FROM cidades WHERE ativa = True")
    cidades_lista = [row['nome'] for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM fontes")
    fontes = cursor.fetchall()
    scraper = cloudscraper.create_scraper()
    for fonte in fontes:
        if fonte['tipo'] == 'HTML':
            processar_html(fonte, cidades_lista, cursor, db, scraper)
        elif fonte['tipo'] == 'RSS':
            processar_rss(fonte, cidades_lista, cursor, db, scraper)
    cursor.close()
    db.close()
    print(f"[{datetime.datetime.now()}] Varredura concluída.")

def loop_automacao():
    while True:
        try:
            varredura_inteligente()
        except Exception as e:
            print(f"Erro no loop: {e}")
        time.sleep(1800)

def iniciar_robo():
    thread = threading.Thread(target=loop_automacao, daemon=True)
    thread.start()
    print("Robô de coleta com resumo IA iniciado!")