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
    except Exception:
        return None

def init_db():
    conn = get_connection(use_database=False)
    if not conn: return
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}")
    cursor.close()
    conn.close()

    conn = get_connection()
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
            preferencias VARCHAR(255) DEFAULT NULL,
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
            titulo VARCHAR(255), 
            resumo TEXT,
            url_original VARCHAR(255) UNIQUE, 
            categoria VARCHAR(50),
            data_publicacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (fonte_id) REFERENCES fontes(id)
        )"""
    ]
    for sql in tabelas:
        cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    