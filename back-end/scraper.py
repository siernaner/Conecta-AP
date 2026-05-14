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
    # Filtro absoluto via regex boundaries (\b) para impedir falsos positivos por substrings
    if re.search(r'\b(polícia|preso|acidente|roubo|bombeiros|pm|furto|crime|investigação|morte|assassinato|tráfico|drogas|colisão|capotar)\b', texto): return 'Segurança Pública'
    if re.search(r'\b(futebol|campeonato|torneio|time|atleta|jogo|esporte|copa|medalha)\b', texto): return 'Esporte'
    if re.search(r'\b(prefeitura|câmara|vereadores|imposto|obras|projeto|licitação|prefeito|governo|iptu|política)\b', texto): return 'Cidadania'
    if re.search(r'\b(saúde|hospital|médico|dengue|vacina|ubs|paciente|remédio|campanha|doença|vírus|leishmaniose)\b', texto): return 'Saúde'
    if re.search(r'\b(educação|escola|aluno|professor|ensino|faculdade|creche|universidade|unesp|fatec|etec)\b', texto): return 'Educação'
    if re.search(r'\b(festa|show|evento|festival|programação|ingresso|exposição|cultura|música)\b', texto): return 'Eventos'
    if re.search(r'\b(agronegócio|safra|soja|rural|colheita|gado|chuva|plantio|fazenda|agricultura)\b', texto): return 'Agronegócio'
    return 'Notícias Gerais'

def varredura_inteligente():
    db = get_connection()
    if not db: return
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT nome FROM cidades WHERE ativa = True")
    cidades = [row['nome'].lower() for row in cursor.fetchall()]

    cursor.execute("SELECT COUNT(*) as total FROM noticias")
    banco_vazio = cursor.fetchone()['total'] == 0
    limite_dias = 7 if banco_vazio else 1
    data_limite = datetime.datetime.now() - datetime.timedelta(days=limite_dias)

    cursor.execute("SELECT * FROM fontes")
    fontes = cursor.fetchall()
    
    for fonte in fontes:
        try:
            if fonte['tipo'] == 'RSS':
                processar_rss(fonte, cidades, data_limite, cursor, db)
            elif fonte['tipo'] == 'HTML':
                processar_html_heuristico(fonte, cursor, db)
        except Exception as e:
            pass
            
    cursor.execute("DELETE FROM noticias WHERE data_publicacao < NOW() - INTERVAL 1 MONTH")
    db.commit()
    cursor.close()
    db.close()

def processar_rss(fonte, cidades, data_limite, cursor, db):
    feed = feedparser.parse(fonte['url'])
    for entry in feed.entries:
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            data_pub = datetime.datetime.fromtimestamp(time.mktime(entry.published_parsed))
        else:
            data_pub = datetime.datetime.now()

        if data_pub < data_limite: continue

        texto_limpo = BeautifulSoup(entry.description, "html.parser").get_text(strip=True)
        texto_completo = f"{entry.title} {texto_limpo}".lower()

        # Validação rigorosa do Fallback: Se for G1, bloqueia a menos que haja match absoluto do município
        if 'g1' in (fonte['nome'] or '').lower():
            citou_cidade = False
            for cidade in cidades:
                if re.search(fr'\b{re.escape(cidade)}\b', texto_completo):
                    citou_cidade = True
                    break
            if not citou_cidade:
                continue 

        resumo_curto = texto_limpo[:200] + '...' if len(texto_limpo) > 200 else texto_limpo
        categoria = classificar_categoria(texto_completo)

        sql = "INSERT IGNORE INTO noticias (fonte_id, titulo, resumo, url_original, categoria, data_publicacao) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (fonte['id'], entry.title, resumo_curto, entry.link, categoria, data_pub))
        db.commit()

def processar_html_heuristico(fonte, cursor, db):
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
                    
                categoria = classificar_categoria(titulo)
                try:
                    sql = "INSERT IGNORE INTO noticias (fonte_id, titulo, resumo, url_original, categoria) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, (fonte['id'], titulo, "Acesse para ler na íntegra no portal oficial.", link, categoria))
                    db.commit()
                    noticias_salvas += 1
                except: pass
    except: pass

def loop_automacao():
    while True:
        varredura_inteligente()
        time.sleep(1800)

def iniciar_robo():
    thread = threading.Thread(target=loop_automacao, daemon=True)
    thread.start()