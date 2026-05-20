import time
import requests
import feedparser
import threading
import datetime
import re
from bs4 import BeautifulSoup
from database import get_connection

def classificar_categoria(texto):
    texto = texto.lower()
    if re.search(r'\b(alagamento|chuva|granizo|temporal|clima|estragos|defesa civil|deslizamento|enchente)\b', texto): return 'Cidadania'
    if re.search(r'\b(polícia|preso|acidente|roubo|bombeiros|furto|crime|investigação|homicídio|assassinato|tráfico|drogas|colisão|capotar)\b', texto): return 'Segurança Pública'
    if re.search(r'\b(futebol|campeonato|torneio|atleta|esporte|copa|medalha|olimpíadas|brasileirão)\b', texto): return 'Esporte'
    if re.search(r'\b(prefeitura|câmara|vereadores|imposto|obras|licitação|prefeito|governo|iptu|política)\b', texto): return 'Cidadania'
    if re.search(r'\b(saúde|hospital|médico|dengue|vacina|ubs|paciente|remédio|campanha|doença|vírus|leishmaniose)\b', texto): return 'Saúde'
    if re.search(r'\b(educação|escola|aluno|professor|ensino|faculdade|creche|universidade|unesp|fatec|etec)\b', texto): return 'Educação'
    if re.search(r'\b(festa|show|evento|festival|ingresso|exposição|cultura|música)\b', texto): return 'Eventos'
    if re.search(r'\b(agronegócio|safra|soja|rural|colheita|gado|chuva|plantio|fazenda|agricultura)\b', texto): return 'Agronegócio'
    return 'Geral'

def extrair_cidade(titulo, corpo, cidades_lista):
    texto_titulo = titulo.lower()
    encontradas_titulo = set()
    
    for cidade in cidades_lista:
        if re.search(fr'\b{re.escape(cidade.lower())}\b', texto_titulo):
            encontradas_titulo.add(cidade)
            
    if len(encontradas_titulo) == 1:
        return list(encontradas_titulo)[0]
        
    texto_corpo = corpo.lower() if corpo else ""
    texto_completo = f"{texto_titulo} {texto_corpo}"
    encontradas_texto = set()
    
    for cidade in cidades_lista:
        if re.search(fr'\b{re.escape(cidade.lower())}\b', texto_completo):
            encontradas_texto.add(cidade)
            
    if len(encontradas_texto) == 1:
        return list(encontradas_texto)[0]
    elif len(encontradas_texto) > 1:
        return 'Região Alta Paulista'
    else:
        return 'Outras Regiões'

def formatar_data_html(soup):
    meta_pub = soup.find('meta', property='article:published_time') or soup.find('meta', attrs={'itemprop': 'datePublished'})
    if meta_pub and meta_pub.get('content'):
        try: 
            return re.sub(r'T', ' ', meta_pub['content'][:19])
        except: 
            pass
    return None

def processar_resumo(titulo, resumo_bruto):
    if not resumo_bruto:
        return "Acesse para ler na íntegra."
        
    resumo = re.sub(fr'^{re.escape(titulo)}', '', resumo_bruto, flags=re.IGNORECASE).strip()
    resumo = re.sub(r'^[\-\|:\s]+', '', resumo)
    
    if len(resumo) > 160:
        resumo = resumo[:157]
        resumo = resumo.rsplit(' ', 1)[0] + "..."
        
    return resumo if resumo else "Acesse para ler na íntegra."

def buscar_corpo_noticia(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            data_encontrada = formatar_data_html(soup)
            
            meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', property='og:description')
            resumo_oficial = meta_desc['content'] if meta_desc and meta_desc.get('content') else ""
            
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'noscript']):
                tag.decompose()
                
            for tag in soup.find_all(attrs={'class': re.compile(r'menu|nav|footer|sidebar|share|social|comments|cookie', re.I)}):
                tag.decompose()
            for tag in soup.find_all(attrs={'id': re.compile(r'menu|nav|footer|sidebar|share|social|comments|cookie', re.I)}):
                tag.decompose()

            article = soup.find('article') or soup.find('main') or soup.body
            
            if not resumo_oficial and article:
                paragrafos = article.find_all('p')
                for p in paragrafos:
                    texto_p = p.get_text(separator=' ', strip=True)
                    if len(texto_p) > 50:
                        resumo_oficial = texto_p
                        break

            texto_limpo = article.get_text(separator=' ', strip=True) if article else ""
            texto_limpo = re.sub(r'\s+', ' ', texto_limpo)
            
            return texto_limpo, data_encontrada, resumo_oficial
    except:
        return "", None, ""
    return "", None, ""

def processar_html(fonte, cidades_lista, cursor, db):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(fonte['url'], headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        cabecalhos = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        noticias_salvas = 0
        
        for elemento in cabecalhos:
            if noticias_salvas >= 10: break
            link_tag = elemento.find('a') if elemento.find('a') else (elemento if elemento.name == 'a' else None)
            if not link_tag: continue
                    
            titulo = link_tag.get_text(strip=True)
            if len(titulo) > 25:
                link = link_tag.get('href')
                if not link: continue
                if not link.startswith('http'):
                    dominio_base = '/'.join(fonte['url'].split('/')[:3])
                    link = dominio_base + '/' + link.lstrip('/')
                
                corpo_completo, data_html, resumo_extraiddo = buscar_corpo_noticia(link)
                cidade_mencionada = extrair_cidade(titulo, corpo_completo, cidades_lista)
                    
                categoria = classificar_categoria(f"{titulo} {corpo_completo}")
                
                resumo_base = resumo_extraiddo if resumo_extraiddo else corpo_completo
                resumo = processar_resumo(titulo, resumo_base)
                
                data_publicacao = data_html if data_html else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data_importacao = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                try:
                    sql = """INSERT IGNORE INTO noticias 
                             (fonte_id, cidade_mencionada, titulo, resumo, corpo_completo, url_original, categoria, data_publicacao, data_importacao) 
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (fonte['id'], cidade_mencionada, titulo, resumo, corpo_completo, link, categoria, data_publicacao, data_importacao))
                    db.commit()
                    noticias_salvas += 1
                except:
                    pass
    except Exception as e:
        print(f"Erro no processamento HTML da fonte {fonte.get('id')}: {e}")

def processar_rss(fonte, cidades_lista, cursor, db):
    try:
        feed = feedparser.parse(fonte['url'])
        noticias_salvas = 0
        for entry in feed.entries:
            if noticias_salvas >= 10: break
            titulo = entry.title
            link = entry.link
            
            corpo_completo, _, resumo_html = buscar_corpo_noticia(link)
            cidade_mencionada = extrair_cidade(titulo, corpo_completo, cidades_lista)
                
            categoria = classificar_categoria(f"{titulo} {corpo_completo}")
            
            descricao_bruta = entry.get('description', '')
            resumo_limpo = BeautifulSoup(descricao_bruta, "html.parser").get_text(strip=True)
            resumo_base = resumo_limpo if resumo_limpo else (resumo_html if resumo_html else corpo_completo)
            resumo = processar_resumo(titulo, resumo_base)
            
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
                cursor.execute(sql, (fonte['id'], cidade_mencionada, titulo, resumo, corpo_completo, link, categoria, data_publicacao, data_importacao))
                db.commit()
                noticias_salvas += 1
            except:
                pass
    except Exception as e:
        print(f"Erro no processamento RSS da fonte {fonte.get('id')}: {e}")

def varredura_inteligente():
    print(f"[{datetime.datetime.now()}] Iniciando varredura de notícias...")
    db = get_connection()
    if not db:
        print("Erro: Não foi possível conectar ao banco de dados")
        return
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT nome FROM cidades WHERE ativa = True")
    cidades_lista = [row['nome'] for row in cursor.fetchall()]

    cursor.execute("SELECT * FROM fontes")
    fontes = cursor.fetchall()
    
    for fonte in fontes:
        if fonte['tipo'] == 'HTML':
            processar_html(fonte, cidades_lista, cursor, db)
        elif fonte['tipo'] == 'RSS':
            processar_rss(fonte, cidades_lista, cursor, db)
            
    cursor.close()
    db.close()
    print(f"[{datetime.datetime.now()}] Varredura concluída!")

def loop_automacao():
    while True:
        try:
            varredura_inteligente()
        except Exception as e:
            print(f"Erro no loop de automação: {e}")
        time.sleep(1800)

def iniciar_robo():
    thread = threading.Thread(target=loop_automacao, daemon=True)
    thread.start()
    print("Robô de coleta de notícias iniciado!")