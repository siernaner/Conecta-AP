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

load_dotenv()

# ==================== CONFIGURAÇÃO GEMINI ====================
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai_client = genai.Client(api_key=GEMINI_API_KEY)
    MODELO_GEMINI = 'gemini-3.1-flash-lite'
else:
    genai_client = None
    print("⚠️ GEMINI_API_KEY não encontrada. Resumos IA desabilitados.")

def resumir_com_gemini(titulo, corpo, max_caracteres=150, tentativas=3):
    """Gera resumo curto com retry em caso de erro."""
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
    
    for tentativa in range(tentativas):
        try:
            response = genai_client.models.generate_content(
                model=MODELO_GEMINI,
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
        except Exception as e:
            print(f"Erro no resumo IA (tentativa {tentativa+1}): {e}")
            if tentativa < tentativas - 1:
                time.sleep(2 ** tentativa)  # backoff exponencial: 1, 2, 4 segundos
    return None

# ==================== FUNÇÕES AUXILIARES ====================
def classificar_categoria(texto):
    texto = texto.lower()
    if re.search(r'\b(alagamento|chuva|granizo|temporal|clima|estragos|defesa civil|deslizamento|enchente)\b', texto): return 'Clima'
    if re.search(r'\b(polícia|preso|roubo|bombeiros|furto|crime|investigação|homicídio|assassinato|tráfico|drogas)\b', texto): return 'Segurança Pública'
    if re.search(r'\b(futebol|campeonato|torneio|atleta|esporte|copa|medalha|olimpíadas|brasileirão)\b', texto): return 'Esporte'
    if re.search(r'\b(prefeitura|câmara|vereadores|imposto|obras|licitação|prefeito|governo|iptu|política)\b', texto): return 'Cidadania'
    if re.search(r'\b(saúde|hospital|médico|dengue|vacina|ubs|paciente|remédio|campanha|doença|vírus|leishmaniose)\b', texto): return 'Saúde'
    if re.search(r'\b(educação|escola|aluno|professor|ensino|faculdade|creche|universidade|unesp|fatec|etec)\b', texto): return 'Educação'
    if re.search(r'\b(festa|show|evento|festival|ingresso|exposição|música)\b', texto): return 'Eventos'
    if re.search(r'\b(agronegócio|safra|soja|rural|colheita|gado|plantio|fazenda|agricultura)\b', texto): return 'Agronegócio'
    if re.search(r'\b(empreendedorismo|tecnologia|inovação|startup|negócios|economia|finanças|investimento|mercado)\b', texto): return 'Negócios'
    if re.search(r'\b(cultura|tradição|folclore|história|patrimônio|turismo|gastronomia)\b', texto): return 'Cultura'
    if re.search(r'\b(colisão|trânsito|acidente|rodovia|estrada|congestionamento|viagem|transporte)\b', texto): return 'Trânsito'
    if re.search(r'\b(ambiente|sustentabilidade|meio ambiente|reciclagem|poluição|desmatamento|conservação)\b', texto): return 'Meio Ambiente'
    if re.search(r'\b(cotidiano|comportamento|saúde mental|lifestyle|moda|culinária|hobby|viagem)\b', texto): return 'Cotidiano'
    if re.search(r'\b(ciência|pesquisa|tecnologia|inovação|universidade|descoberta|espaço|saúde)\b', texto): return 'Ciência e Tecnologia'
    return 'Geral'

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