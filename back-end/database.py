import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection(use_database=True):
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME') if use_database else None,
            auth_plugin='mysql_native_password'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Erro na conexão com o banco: {err}")
        return None

def init_db():
    try:
        conn = get_connection(use_database=False)
        if not conn:
            print("Falha ao conectar ao MySQL")
            return
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}")
        cursor.close()
        conn.close()

        conn = get_connection()
        if not conn:
            print("Falha ao conectar ao banco de dados")
            return
        cursor = conn.cursor()
        
        tabelas = [
            """CREATE TABLE IF NOT EXISTS cidades (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) UNIQUE,
                ativa BOOLEAN DEFAULT TRUE
            )""",
            """CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100), 
                email VARCHAR(100) UNIQUE,
                senha_hash VARCHAR(255) NOT NULL,
                role ENUM('admin', 'user') DEFAULT 'user',
                ativo BOOLEAN DEFAULT TRUE,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS fontes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cidade_id INT,
                nome VARCHAR(100), 
                url VARCHAR(255),
                tipo ENUM('RSS', 'HTML') DEFAULT 'RSS',
                FOREIGN KEY (cidade_id) REFERENCES cidades(id)
            )""",
            """CREATE TABLE IF NOT EXISTS noticias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fonte_id INT, 
                cidade_mencionada VARCHAR(100),
                titulo VARCHAR(255), 
                resumo TEXT,
                corpo_completo TEXT,
                url_original VARCHAR(255) UNIQUE, 
                categoria VARCHAR(50),
                oculto BOOLEAN DEFAULT FALSE,
                data_publicacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_importacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fonte_id) REFERENCES fontes(id)
            )""",
            """CREATE TABLE IF NOT EXISTS noticias_lidas (
                usuario_id INT,
                noticia_id INT,
                status_noticia VARCHAR(20) DEFAULT 'VISTA',
                hora_aberta TIMESTAMP NULL,
                PRIMARY KEY (usuario_id, noticia_id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                FOREIGN KEY (noticia_id) REFERENCES noticias(id) ON DELETE CASCADE
            )"""
        ]
        for sql in tabelas:
            cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
        print("Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"Erro na inicialização do banco: {e}")