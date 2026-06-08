import psycopg2
from config import DB_CONFIG
import logging


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def create_table():
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'chat_history'
            );
        """)

        exists = cur.fetchone()[0]

        if exists:
            logging.info("chat_history table already exists")
        else:
            cur.execute("""
                CREATE TABLE chat_history (
                    id SERIAL PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

            logging.info("chat_history table created")

        cur.close()

    except Exception as e:
        logging.error(f"Create table error: {e}")

    finally:
        if conn:
            conn.close()


def save_chat(question, answer):
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO chat_history(question, answer)
            VALUES (%s, %s)
            """,
            (question, answer)
        )

        conn.commit()

        cur.close()

    except Exception as e:
        logging.error(f"DB Error: {e}")

    finally:
        if conn:
            conn.close()


def get_chat_history(limit=20):
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT question, answer, created_at
            FROM chat_history
            ORDER BY id DESC
            LIMIT %s
            """,
            (limit,)
        )

        rows = cur.fetchall()

        cur.close()

        return rows

    except Exception as e:
        logging.error(f"DB Error: {e}")
        return []

    finally:
        if conn:
            conn.close()