import bcrypt
import unicodedata
from database import get_connection, init_db

def gerar_hash(senha):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')

def formatar_url_cidade(nome):
    especiais = {
        'Arco-Íris': 'arcoiris',
        'São João do Pau d\'Alho': 'paudalho',
    }
    if nome in especiais:
        slug = especiais[nome]
    else:
        sem_acentos = ''.join(c for c in unicodedata.normalize('NFD', nome) if unicodedata.category(c) != 'Mn')
        slug = sem_acentos.replace(' ', '').lower()
        slug = slug.replace('-', '')
    return f"https://www.{slug}.sp.gov.br"

def popular_sistema():
    init_db() 
    db = get_connection()
    if not db: 
        print("Erro ao conectar ao banco")
        return
    cursor = db.cursor()

    cidades = [
        'Adamantina', 'Arco-Íris', 'Bastos', 'Dracena', 'Flórida Paulista', 
        'Garça', 'Herculândia', 'Iacri', 'Irapuru', 'Junqueirópolis', 
        'Lucélia', 'Mariápolis', 'Marília', 'Monte Castelo', 'Nova Guataporanga', 
        'Oriente', 'Osvaldo Cruz', 'Ouro Verde', 'Pacaembu', 'Panorama', 
        'Parapuã', 'Paulicéia', 'Pompeia', 'Pracinha', 'Queiroz', 
        'Quintana', 'Rinópolis', 'Sagres', 'Salmourão', 'Santa Mercedes', 
        "São João do Pau d'Alho", 'Tupã', 'Tupi Paulista', 'Vera Cruz'
    ]
    
    # Insere cidades e suas prefeituras (como fontes com cidade_id)
    for cidade in cidades:
        cursor.execute("INSERT IGNORE INTO cidades (nome, ativa) VALUES (%s, True)", (cidade,))
        cursor.execute("SELECT id FROM cidades WHERE nome = %s", (cidade,))
        cidade_id = cursor.fetchone()[0]
        url_prefeitura = formatar_url_cidade(cidade)
        cursor.execute("INSERT IGNORE INTO fontes (cidade_id, nome, url, tipo) VALUES (%s, %s, %s, %s)", 
                       (cidade_id, f"Prefeitura de {cidade}", url_prefeitura, 'HTML'))

    # Portais regionais (sem incluir as prefeituras novamente)
    portais_regionais = [
        ('Marília Notícia', 'https://marilianoticia.com.br/', 'HTML'),
        ('Garça em Foco', 'https://garcaemfoco.com.br/', 'HTML'),
        ('Bastos Já', 'https://www.bastosja.com.br/', 'HTML'),
        ('TupãCity', 'https://www.tupacity.com/', 'HTML'),
        ('Siga Mais', 'https://sigamais.com/', 'HTML'),
        ('Jornal Interativo', 'https://jornalinterativo.net/', 'HTML'),
        ('O Dia de Marília', 'https://odiademarilia.com.br/', 'HTML'),
        ('Portal Regional', 'https://www.portalregional.net.br/', 'HTML'),
        ('G1 Regional', 'https://g1.globo.com/rss/g1/sp/bauru-marilia/', 'RSS')
    ]

    for nome_fonte, url, tipo in portais_regionais:
        cursor.execute("INSERT IGNORE INTO fontes (nome, url, tipo) VALUES (%s, %s, %s)", (nome_fonte, url, tipo))

    # Usuários
    usuarios = [
        {"nome": "cidadecoracao", "email": "master@conecta.com.br", "senha": "Asdf1234!", "role": "admin"},
        {"nome": "userpompeia", "email": "user@conecta.com.br", "senha": "0987654Ee", "role": "user"}
    ]

    for user in usuarios:
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (user['email'],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO usuarios (nome, email, senha_hash, role) VALUES (%s, %s, %s, %s)",
                           (user['nome'], user['email'], gerar_hash(user['senha']), user['role']))

    db.commit()
    cursor.close()
    db.close()
    print("Banco populado com sucesso!")

if __name__ == "__main__":
    popular_sistema()