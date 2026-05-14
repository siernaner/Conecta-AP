import os
import re
import bcrypt
import jwt
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
from database import init_db, get_connection
from scraper import iniciar_robo
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
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

def validar_forca_senha(senha):
    if len(senha) < 8: return False
    if not re.search(r"[A-Z]", senha): return False
    if not re.search(r"[a-z]", senha): return False
    if not re.search(r"\d", senha): return False
    return True

@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT id, nome, senha_hash, role, preferencias FROM usuarios WHERE email = %s", (dados.get('email'),))
    usuario = cursor.fetchone()
    
    if not usuario or not bcrypt.checkpw(dados.get('senha', '').encode('utf-8'), usuario['senha_hash'].encode('utf-8')):
        cursor.close()
        db.close()
        return jsonify({'erro': 'credenciais_invalidas'}), 401
        
    token = jwt.encode({
        'id': usuario['id'],
        'role': usuario['role'],
        'nome': usuario['nome'],
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
    }, os.getenv('JWT_SECRET'), algorithm='HS256')
    
    preferencias = usuario['preferencias']
    cursor.close()
    db.close()
    
    return jsonify({
        'token': token, 
        'role': usuario['role'], 
        'nome': usuario['nome'],
        'preferencias': preferencias
    })

@app.route('/registro', methods=['POST'])
def registro():
    dados = request.get_json()
    senha = dados.get('senha')
    
    if not validar_forca_senha(senha):
        return jsonify({'erro': 'senha_fraca'}), 400
        
    hash_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    db = get_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (%s, %s, %s)", 
            (dados.get('nome'), dados.get('email'), hash_senha)
        )
        db.commit()
        return jsonify({'msg': 'sucesso'}), 201
    except Exception:
        return jsonify({'erro': 'erro_cadastro'}), 400
    finally:
        cursor.close()
        db.close()

@app.route('/preferencias', methods=['POST'])
@token_required
def salvar_preferencias():
    dados = request.get_json()
    temas = dados.get('temas', [])
    temas_str = ','.join(temas) if temas else ''
    
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE usuarios SET preferencias = %s WHERE id = %s", (temas_str, request.usuario_logado['id']))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'msg': 'sucesso'})

@app.route('/noticias', methods=['GET'])
def get_noticias():
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM noticias ORDER BY data_publicacao DESC LIMIT 100")
    noticias = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(noticias)

if __name__ == '__main__':
    init_db()
    iniciar_robo()
    app.run(port=5001, debug=True, use_reloader=False)