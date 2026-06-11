import psycopg2
# from config import DB_CONFIG
from config import DATABASE_URL
import logging


def get_connection():

    # OLD
    # return psycopg2.connect(
    #     **DB_CONFIG,
    #     connect_timeout=10
    # )

    return psycopg2.connect(
        DATABASE_URL,
        connect_timeout=10
    )


def create_table():
    conn = None

    try:
        conn = get_connection()

        # OLD
        # cur = conn.cursor()

        with conn.cursor() as cur:

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

        # OLD
        # cur.close()

    except Exception as e:
        if conn:
            conn.rollback()

        logging.error(f"Create table error: {e}")

    finally:
        if conn:
            conn.close()


def save_chat(question, answer):
    conn = None

    try:
        logging.info("save_chat called")

        conn = get_connection()

        # OLD
        # cur = conn.cursor()

        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO chat_history(question, answer)
                VALUES (%s, %s)
                """,
                (question, answer)
            )

            conn.commit()

            logging.info("chat saved successfully")

        # OLD
        # cur.close()

    except Exception as e:
        if conn:
            conn.rollback()

        logging.error(f"DB Error: {e}")

    finally:
        if conn:
            conn.close()


def get_chat_history(limit=20):
    conn = None

    try:
        conn = get_connection()

        # OLD
        # cur = conn.cursor()

        with conn.cursor() as cur:

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

        # OLD
        # cur.close()

        return rows

    except Exception as e:
        logging.error(f"DB Error: {e}")
        return []

    finally:
        if conn:
            conn.close()