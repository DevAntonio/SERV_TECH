import sqlite3
# Import corrigido para apontar para o módulo db dentro do pacote app.database
from app.database.db import get_conn
import os

# Este arquivo será criado no diretório de onde app.py é executado (provavelmente a raiz)
REMEMBER_FILE = "remember_me.txt"

# ------------------
# Operações de Login
# ------------------
def check_login(username: str, password: str) -> bool:
    """
    Verifica credenciais de acesso usando a tabela de usuários.
    Retorna True/False conforme encontrou registro compatível.
    """
    conn = get_conn()
    cur = conn.cursor()
    # CORREÇÃO DE SEGURANÇA: Usando parâmetros (?) para evitar SQL Injection
    sql = "SELECT id FROM users WHERE username = ? AND password = ?"
    try:
        cur.execute(sql, (username, password))
        row = cur.fetchone()
        return bool(row)
    finally:
        conn.close()

def save_remember_me(user, pw):
    """
    Salva as credenciais localmente para reutilização posterior
    conforme a preferência do usuário.
    """
    try:
        with open(REMEMBER_FILE, "w", encoding="utf-8") as f:
            f.write(f"{user};{pw}")
    except IOError as e:
        print(f"Erro ao salvar remember_me: {e}") # Log de erro

# ------------------
# Operações de Ordem
# ------------------
def upsert_order(cliente: str, descricao: str, preco_str: str, status: str):
    """
    Insere um novo registro de ordem de serviço com os dados informados.
    (Nota: Esta função apenas insere, não atualiza (update) de fato)
    """
    conn = get_conn()
    cur = conn.cursor()
    # CORREÇÃO DE SEGURANÇA: Usando parâmetros (?) para evitar SQL Injection
    sql = "INSERT INTO orders (cliente, descricao, preco, status) VALUES (?, ?, ?, ?)"
    try:
        cur.execute(sql, (cliente, descricao, preco_str, status))
        conn.commit()
    finally:
        conn.close()

def delete_order(order_id):
    """
    Remove o registro de ordem associado ao ID informado.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Usando parâmetro (?) por segurança
        cur.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        conn.commit()
    finally:
        conn.close()

def list_orders():
    """
    Retorna os registros de ordens em ordem decrescente por ID.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, cliente, descricao, preco, status FROM orders ORDER BY id DESC")
        rows = cur.fetchall()
        return rows
    finally:
        conn.close()

def search_orders(termo: str):
    """
    Retorna os registros filtrados pelo nome do cliente informado.
    """
    conn = get_conn()
    cur = conn.cursor()
    # CORREÇÃO DE SEGURANÇA: Usando parâmetros (?) para evitar SQL Injection
    sql = "SELECT id, cliente, descricao, preco, status FROM orders WHERE cliente LIKE ? ORDER BY id DESC"
    try:
        cur.execute(sql, (f'%{termo}%',)) # Adiciona % ao redor do parâmetro
        rows = cur.fetchall()
        return rows
    finally:
        conn.close()
