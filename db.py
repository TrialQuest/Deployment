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