
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
            cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE';
             """)
            result = cursor.fetchall()

            print("Database connected successfully!")
            for table in result:
                print(table[0])

except psycopg.Error as error:
    print("Database connection failed.")
    print(type(error).__name__)
    print(str(error))
