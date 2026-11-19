
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")

sql_file = (
    Path(__file__).resolve().parent.parent
    / "sql"
    / "schema.sql"
)

sql = sql_file.read_text()

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cursor:
        cursor.execute(sql)

print("Database tables created successfully!")
