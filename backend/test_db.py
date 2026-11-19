
import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is missing")

try:
    with psycopg.connect(
        database_url,
        connect_timeout=10
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            result = cursor.fetchone()

            print("Database connected successfully!")
            print(result[0])

except psycopg.Error as error:
    print("Database connection failed.")
    print(type(error).__name__)
    print(str(error))
