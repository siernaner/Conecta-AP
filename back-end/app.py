import os
import re
import bcrypt
import jwt
import datetime
import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from database import init_db, get_connection
from scraper import iniciar_robo
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

# ==================== DECORATORS ====================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return jsonify({}), 200
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'erro': 'unauthorized'}), 401
        try:
            token = token.split(" ")[1]
            dados = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
            request.usuario_logado = dados
        except Exception:
            return jsonify({'erro': 'unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return jsonify({}), 200
        if request.usuario_logado.get('role') != 'admin':
            return jsonify({'erro': 'Acesso negado'}), 403
        return f(*args, **kwargs)
    return decorated

# ==================== ROTAS PÚBLICAS ====================
@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    dados = request.get_json(force=True, silent=True) or {}
    email = dados.get('email')
    senha = dados.get('senha')
    if not email or not senha:
        return jsonify({'erro': 'email_e_senha_obrigatorios'}), 400
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    u = cursor.fetchone()
    if u and bcrypt.checkpw(senha.encode('utf-8'), u['senha_hash'].encode('utf-8')):
        if not u.get('ativo', True):
            cursor.close()
            db.close()
            return jsonify({'erro': 'conta_bloqueada'}), 403
        token = jwt.encode({
            'id': u['id'],
            'role': u['role'],
            'nome': u['nome'],
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
        }, os.getenv('JWT_SECRET'), algorithm='HS256')
        cursor.close()
        db.close()
        return jsonify({
            'token': token,
            'role': u['role'],
            'nome': u['nome'],
            'id': u['id']
        })
    cursor.close()
    db.close()
    return jsonify({'erro': 'credenciais_invalidas'}), 401

@app.route('/registro', methods=['POST', 'OPTIONS'])
def registrar():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    dados = request.get_json(force=True, silent=True) or {}
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    if not nome or not email or not senha:
        return jsonify({'erro': 'campos_obrigatorios'}), 400
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({'erro': 'email_invalido'}), 400
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', senha):
        return jsonify({'erro': 'senha_fraca'}), 400
    db = get_connection()
    cursor = db.cursor()
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, role) VALUES (%s, %s, %s, 'user')",
            (nome, email, senha_hash)
        )
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'msg': 'usuario_criado'}), 201
    except mysql.connector.IntegrityError:
        cursor.close()
        db.close()
        return jsonify({'erro': 'email_existente'}), 409
    except Exception:
        cursor.close()
        db.close()
        return jsonify({'erro': 'erro_interno'}), 500

@app.route('/noticias', methods=['GET', 'OPTIONS'])
def get_noticias():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    search = request.args.get('search', '')
    usuario_id = request.args.get('u_id')
    if usuario_id == 'undefined' or usuario_id == '':
        usuario_id = None
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    params = []
    query_where = "WHERE n.cidade_mencionada IS NOT NULL AND COALESCE(n.oculto, 0) = 0 "
    if search:
        query_where += " AND (n.titulo LIKE %s OR n.resumo LIKE %s OR n.corpo_completo LIKE %s) "
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    if usuario_id:
        sql = f"""
            SELECT n.*, f.nome AS fonte_nome, n.cidade_mencionada AS cidade,
            COALESCE(nl.status_noticia, 'NOVA') as status_leitura
            FROM noticias n
            JOIN fontes f ON n.fonte_id = f.id
            LEFT JOIN noticias_lidas nl ON nl.noticia_id = n.id AND nl.usuario_id = %s
            {query_where}
            ORDER BY n.id DESC
        """
        params_final = [int(usuario_id)] + params
    else:
        sql = f"""
            SELECT n.*, f.nome AS fonte_nome, n.cidade_mencionada AS cidade, 'NOVA' as status_leitura
            FROM noticias n
            JOIN fontes f ON n.fonte_id = f.id
            {query_where}
            ORDER BY n.id DESC
        """
        params_final = params
    cursor.execute(sql, params_final)
    noticias = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(noticias)

# ==================== ROTAS AUTENTICADAS ====================
@app.route('/noticias/marcar-vistas', methods=['POST', 'OPTIONS'])
@token_required
def marcar_vistas():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    dados = request.get_json(force=True, silent=True) or {}
    ids = dados.get('ids', [])
    u_id = dados.get('u_id')
    if not u_id or not ids:
        return jsonify({'msg': 'dados invalidos'}), 400
    db = get_connection()
    cursor = db.cursor()
    for n_id in ids:
        cursor.execute("""
            INSERT IGNORE INTO noticias_lidas (usuario_id, noticia_id, status_noticia)
            VALUES (%s, %s, 'VISTA')
        """, (int(u_id), int(n_id)))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'msg': 'ok'})

@app.route('/noticias/marcar-aberta', methods=['POST', 'OPTIONS'])
@token_required
def marcar_aberta():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    dados = request.get_json(force=True, silent=True) or {}
    n_id = dados.get('id')
    u_id = dados.get('u_id')
    if not u_id or not n_id:
        return jsonify({'msg': 'dados invalidos'}), 400
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO noticias_lidas (usuario_id, noticia_id, status_noticia, hora_aberta)
        VALUES (%s, %s, 'ABERTA', CURRENT_TIMESTAMP)
        ON DUPLICATE KEY UPDATE status_noticia = 'ABERTA', hora_aberta = CURRENT_TIMESTAMP
    """, (int(u_id), int(n_id)))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'msg': 'ok'})

# ==================== ROTAS ADMIN ====================
@app.route('/admin/usuarios', methods=['GET', 'OPTIONS'])
@admin_required
def admin_get_usuarios():
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, email, role, COALESCE(ativo, 1) as ativo, data_criacao FROM usuarios ORDER BY id DESC")
    usuarios = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(usuarios)

@app.route('/admin/usuarios/<int:id>/bloquear', methods=['POST', 'OPTIONS'])
@admin_required
def admin_toggle_bloqueio(id):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE usuarios SET ativo = NOT COALESCE(ativo, 1) WHERE id = %s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'msg': 'Status alterado'})

@app.route('/admin/usuarios/<int:id>/cargo', methods=['POST', 'OPTIONS'])
@admin_required
def admin_toggle_cargo(id):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE usuarios SET role = IF(role='admin', 'user', 'admin') WHERE id = %s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'msg': 'Cargo alterado'})

@app.route('/admin/cidades_fontes', methods=['GET', 'OPTIONS'])
@admin_required
def admin_get_cidades_fontes():
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cidades ORDER BY nome")
    cidades = cursor.fetchall()
    cursor.execute("""
        SELECT f.*, c.nome as cidade_nome
        FROM fontes f
        LEFT JOIN cidades c ON f.cidade_id = c.id
        ORDER BY f.id DESC
    """)
    fontes = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify({'cidades': cidades, 'fontes': fontes})

@app.route('/admin/fontes', methods=['POST', 'OPTIONS'])
@admin_required
def admin_add_fonte():
    d = request.get_json(force=True, silent=True) or {}
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO fontes (nome, url, tipo, cidade_id) VALUES (%s, %s, %s, %s)",
                   (d.get('nome'), d.get('url'), d.get('tipo'), d.get('cidade_id') if d.get('cidade_id') else None))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'msg': 'Fonte adicionada'})

@app.route('/admin/fontes/<int:id>', methods=['DELETE', 'OPTIONS'])
@admin_required
def admin_delete_fonte(id):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE noticias SET oculto = 1 WHERE fonte_id = %s", (id,))
    cursor.execute("DELETE FROM fontes WHERE id = %s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'msg': 'Fonte excluída'})

@app.route('/admin/moderacao', methods=['GET', 'OPTIONS'])
@admin_required
def admin_get_moderacao():
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT n.id, n.titulo, n.data_publicacao, n.cidade_mencionada as cidade, f.nome as fonte_nome, COALESCE(n.oculto, 0) as oculto
        FROM noticias n
        JOIN fontes f ON n.fonte_id = f.id
        ORDER BY n.id DESC
    """)
    noticias = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(noticias)

@app.route('/admin/noticias/<int:id>/toggle', methods=['POST', 'OPTIONS'])
@admin_required
def admin_toggle_noticia(id):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE noticias SET oculto = NOT COALESCE(oculto, 0) WHERE id = %s", (id,))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'msg': 'Visibilidade alterada'})

# ==================== ROTAS DE PERFIL E EDIÇÃO DE USUÁRIOS ====================
@app.route('/usuario/<int:id>', methods=['GET', 'OPTIONS'])
@token_required
def get_usuario(id):
    """Obtém dados de um usuário. Admin pode acessar qualquer; usuário apenas o próprio."""
    if request.usuario_logado['role'] != 'admin' and request.usuario_logado['id'] != id:
        return jsonify({'erro': 'acesso_negado'}), 403
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, nome, email, role, ativo, data_criacao FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()
    cursor.close()
    db.close()
    if not usuario:
        return jsonify({'erro': 'usuario_nao_encontrado'}), 404
    return jsonify(usuario)

@app.route('/usuario/<int:id>', methods=['PUT', 'OPTIONS'])
@token_required
def update_usuario(id):
    """Atualiza nome, email ou senha do usuário. Admin pode atualizar qualquer um; usuário apenas o próprio."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    if request.usuario_logado['role'] != 'admin' and request.usuario_logado['id'] != id:
        return jsonify({'erro': 'acesso_negado'}), 403
    
    dados = request.get_json(force=True, silent=True) or {}
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    
    if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return jsonify({'erro': 'email_invalido'}), 400
    if senha and not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', senha):
        return jsonify({'erro': 'senha_fraca'}), 400
    
    db = get_connection()
    cursor = db.cursor()
    updates = []
    params = []
    if nome:
        updates.append("nome = %s")
        params.append(nome)
    if email:
        updates.append("email = %s")
        params.append(email)
    if senha:
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        updates.append("senha_hash = %s")
        params.append(senha_hash)
    
    if not updates:
        cursor.close()
        db.close()
        return jsonify({'msg': 'nenhuma_alteracao'}), 200
    
    params.append(id)
    sql = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = %s"
    try:
        cursor.execute(sql, params)
        db.commit()
        cursor.close()
        db.close()
        return jsonify({'msg': 'usuario_atualizado'}), 200
    except mysql.connector.IntegrityError:
        cursor.close()
        db.close()
        return jsonify({'erro': 'email_existente'}), 409
    except Exception as e:
        cursor.close()
        db.close()
        return jsonify({'erro': 'erro_interno'}), 500

# ==================== CONFIGURAÇÃO GEMINI ====================
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai_client = genai.Client(api_key=GEMINI_API_KEY)
    # Lista completa com todos os modelos (ordem: maior cota primeiro)
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
    print("Aviso: GEMINI_API_KEY não encontrada. O endpoint /resumir-noticia não funcionará.")

def resumir_com_gemini(titulo, corpo, max_caracteres=150):
    if not genai_client:
        return "Erro: API do Gemini não configurada."

    prompt = f"""Você é um redator de resumos para um portal de notícias.
Gere um resumo curto (máximo {max_caracteres} caracteres) da notícia abaixo.

REGRAS:
1. NÃO repita o título.
2. Adicione uma informação EXTRA que não esteja no título (ex: números, causas, consequências, local detalhado, declarações).
3. Seja direto, em português, sem frases introdutórias.
4. Responda APENAS com o resumo.

TÍTULO: {titulo}

NOTÍCIA: {corpo}

RESUMO:"""

    ultimo_erro = None
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
            # Se resposta vazia, tentar próximo modelo
            continue
        except Exception as e:
            erro_str = str(e)
            # Se o modelo não existe (404) ou quota esgotada (429), pula
            if '404' in erro_str or '429' in erro_str or 'RESOURCE_EXHAUSTED' in erro_str:
                print(f"Modelo {modelo} indisponível: {erro_str[:80]}")
                continue
            # Outros erros (timeout, 503, etc.) também tenta próximo
            print(f"Erro com modelo {modelo}: {erro_str[:80]}")
            ultimo_erro = e
            continue

    # Se todos falharem
    return f"Erro ao gerar resumo: {str(ultimo_erro)}" if ultimo_erro else "Erro ao gerar resumo (todos os modelos falharam)."

# ==================== EXECUÇÃO ====================
if __name__ == '__main__':
    init_db()
    iniciar_robo()
    app.run(port=5001, debug=True, use_reloader=False)