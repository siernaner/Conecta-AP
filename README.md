# 🚆 Conecta Alta Paulista

O **Conecta Alta Paulista** é um agregador automático de notícias focado exclusivamente na região da Alta Paulista. O projeto tem como objetivo rastrear, categorizar e centralizar informações publicadas ao longo de todo o tronco férreo paulista, contemplando os municípios desde **Garça até Panorama**.

## 🚀 Como executar o projeto localmente

Para rodar o projeto do zero, você precisará configurar os ambientes do Backend (Python/MySQL) e Frontend (Next.js/React) em terminais separados.

### 1. Configuração do Backend e Banco de Dados (Terminal 1)

Antes de iniciar, certifique-se de ter o MySQL instalado e o Python 3.12+ configurado.

1.  Navegue até a pasta do backend:
    ```bash
    cd backend
    ```
2.  Crie um arquivo `.env` na raiz da pasta `backend` com suas credenciais:
    ```env
    DB_HOST=localhost
    DB_USER=seu_usuario
    DB_PASSWORD=sua_senha
    DB_NAME=conecta_db
    JWT_SECRET=sua_chave_secreta
    ```
3.  Crie e ative o ambiente virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate  # No Windows: venv\Scripts\activate
    ```
4.  Instale as dependências:
    ```bash
    python -m pip install -r requirements.txt
    ```
5.  Inicialize o banco e as fontes:
    ```bash
    python popular_banco.py
    ```
6.  Inicie a API:
    ```bash
    python app.py
    ```

### 2. Configuração do Frontend (Terminal 2)

Com o backend rodando, abra uma nova aba do terminal.

1.  Navegue até a pasta do frontend:
    ```bash
    cd frontend
    ```
2.  Instale os pacotes do Node:
    ```bash
    npm install
    ```
3.  Inicie o servidor de desenvolvimento:
    ```bash
    npm run dev
    ```
4.  Acesse: **http://localhost:3000**

---

## ⚖️ Disclaimer (Aviso Legal)

Este sistema foi desenvolvido como uma ferramenta prática e possui **fins estritamente educativos e acadêmicos**, não buscando qualquer tipo de lucro, monetização ou viés comercial.

Todas as notícias e resumos veiculados no site têm origens externas e são extraídos de forma automatizada (via RSS e Web Scraping) de portais de notícias regionais e sites oficiais de prefeituras. 

A equipe de desenvolvedores do sistema atua estritamente na elaboração da arquitetura tecnológica. **Os alunos desenvolvedores não possuem opinião embasada sobre os assuntos abordados nas matérias**. O teor, a veracidade e as opiniões expressas nas notícias são de **total e exclusiva responsabilidade dos sites e autores originais** que as publicam.
