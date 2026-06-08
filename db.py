import psycopg2
from config import DB_CONFIG
import logging


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


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
            SELECT question, answer
            FROM chat_history
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