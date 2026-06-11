from groq import Groq
import os
import logging

logging.basicConfig(
    filename="deployment.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

client=Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_env(key: str):
    value = os.getenv(key)
    if not value:
        logging.error(f"Missing ENV variable : {key}")
        raise ValueError(f"Missing ENV variable : {key}")
    return value

DB_CONFIG = {
    "dbname": get_env("DB_NAME1"),
    "user": get_env("DB_USER"),
    "password": get_env("DB_PASSWORD"),
    "host": get_env("DB_HOST"),
    "port": get_env("DB_PORT"),
}

DATABASE_URL = os.getenv("DATABASE_URL")