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

@app.route('/noticias', methods=['GET'])
def get_noticias():
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    # Alterado para ORDER BY n.id DESC, ordenando pela ordem exata em que o robô importou
    sql = """
        SELECT n.*, f.nome AS fonte_nome, 
               COALESCE(n.cidade_mencionada, c.nome, 'Região') AS cidade
        FROM noticias n
        LEFT JOIN fontes f ON n.fonte_id = f.id
        LEFT JOIN cidades c ON f.cidade_id = c.id
        ORDER BY n.id DESC LIMIT 300
    """
    cursor.execute(sql)
    noticias = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(noticias)

if __name__ == '__main__':
    init_db()
    iniciar_robo()
    app.run(port=5001, debug=True, use_reloader=False)