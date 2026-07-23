import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """Abre e fecha a conexão com o PostgreSQL de forma segura em cada requisição."""
    conn = psycopg2.connect(st.secrets["postgres"]["url"])
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Cria a estrutura de tabelas se não existirem."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Tabela de Usuários
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    nome VARCHAR(100) NOT NULL,
                    password_hash TEXT NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Tabela de Vagas vinculada ao Usuário
            cur.execute("""
                CREATE TABLE IF NOT EXISTS vagas (
                    id SERIAL PRIMARY KEY,
                    usuario_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
                    empresa VARCHAR(100) NOT NULL,
                    cargo VARCHAR(100) NOT NULL,
                    salario VARCHAR(50),
                    link TEXT,
                    status VARCHAR(50) DEFAULT 'Aplicado',
                    tags VARCHAR(255),
                    data_aplicacao DATE DEFAULT CURRENT_DATE
                );
            """)
            conn.commit()

def cadastrar_usuario(username, email, nome, password_hash):
    """Cadastra um novo usuário no banco."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO usuarios (username, email, nome, password_hash) VALUES (%s, %s, %s, %s) RETURNING id;",
                    (username.strip().lower(), email.strip().lower(), nome.strip(), password_hash)
                )
                user_id = cur.fetchone()[0]
                conn.commit()
                return True, user_id
    except psycopg2.IntegrityError:
        return False, "Usuário ou E-mail já cadastrado."
    except Exception as e:
        return False, str(e)

def buscar_usuario_por_username(username):
    """Busca dados de login do usuário."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM usuarios WHERE LOWER(username) = LOWER(%s);", (username.strip(),))
            return cur.fetchone()

def buscar_vagas_usuario(usuario_id):
    """Retorna apenas as vagas do usuário logado."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT id, empresa, cargo, salario, status, tags, data_aplicacao, link FROM vagas WHERE usuario_id = %s ORDER BY id DESC;",
                (usuario_id,)
            )
            return cur.fetchall()

def listar_vagas_usuario(usuario_id, busca=""):
    """Lista vagas com suporte a busca direto via SQL."""
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if busca:
                termo = f"%{busca.strip()}%"
                cur.execute(
                    """SELECT id, empresa, cargo, salario, status, tags, data_aplicacao, link 
                       FROM vagas 
                       WHERE usuario_id = %s AND (LOWER(empresa) LIKE LOWER(%s) OR LOWER(cargo) LIKE LOWER(%s))
                       ORDER BY id DESC;""",
                    (usuario_id, termo, termo)
                )
            else:
                cur.execute(
                    "SELECT id, empresa, cargo, salario, status, tags, data_aplicacao, link FROM vagas WHERE usuario_id = %s ORDER BY id DESC;",
                    (usuario_id,)
                )
            return cur.fetchall()

def verificar_duplicado(usuario_id, empresa, cargo):
    """Verifica se o usuário já cadastrou essa vaga específica."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT status, data_aplicacao FROM vagas WHERE usuario_id = %s AND LOWER(empresa) = LOWER(%s) AND LOWER(cargo) = LOWER(%s);",
                (usuario_id, empresa.strip(), cargo.strip())
            )
            return cur.fetchone()

def inserir_vaga(usuario_id, empresa, cargo, salario, link, status, tags, data_app):
    """Insere nova vaga para o usuário."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO vagas (usuario_id, empresa, cargo, salario, link, status, tags, data_aplicacao) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
                (usuario_id, empresa.strip(), cargo.strip(), salario, link, status, tags, data_app)
            )
            conn.commit()

def atualizar_vaga(vaga_id, empresa, cargo, status, link="", anotacoes=""):
    """Atualiza todos os dados de uma vaga existente."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE vagas 
                   SET empresa = %s, cargo = %s, status = %s, link = %s, tags = %s 
                   WHERE id = %s;""",
                (empresa.strip(), cargo.strip(), status, link, anotacoes, vaga_id)
            )
            conn.commit()

def atualizar_status_vaga(usuario_id, vaga_id, novo_status):
    """Atualiza apenas o status de uma vaga garantindo que pertence ao usuário."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE vagas SET status = %s WHERE id = %s AND usuario_id = %s;",
                (novo_status, vaga_id, usuario_id)
            )
            conn.commit()
