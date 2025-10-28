import sqlite3
import os

# Obtém o caminho absoluto para o diretório onde este script (db.py) está localizado
DB_DIR = os.path.abspath(os.path.dirname(__file__))

# Define o caminho completo para o arquivo do banco de dados dentro desse diretório
DB_FILE = os.path.join(DB_DIR, "servtech.db")

def get_conn():
    """
    Abre e retorna uma conexão com o banco SQLite.
    O arquivo é criado no diretório app/database, se ainda não existir.
    """
    # Garante que o diretório (app/database) exista
    os.makedirs(DB_DIR, exist_ok=True)
    return sqlite3.connect(DB_FILE)

def init_db():
    """
    Cria as tabelas básicas (users e orders), caso ainda não existam,
    e insere um usuário inicial para autenticação.
    """
    conn = get_conn()
    cur = conn.cursor()

    # Cadastro de usuários
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # Cadastro de ordens de serviço
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT,
        descricao TEXT,
        preco TEXT,
        status TEXT
    )
    """)

    # Insere um usuário padrão na inicialização (admin/admin123)
    # Verifica se o usuário já existe para evitar duplicatas
    cur.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users (username, password) VALUES ('admin','admin123')")

    conn.commit()
    conn.close()
