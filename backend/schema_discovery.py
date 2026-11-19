import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

def get_tables():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is missing")

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)

            rows = cursor.fetchall()

            tables = [row[0] for row in rows]

            return tables


def get_columns(table_name):
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is missing")

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))

            rows = cursor.fetchall()

            columns = []

            for row in rows:
                columns.append({
                    "name": row[0],
                    "type": row[1]
                })

            return columns

if __name__ == "__main__":
    print("Tables:")
    print(get_tables())

    print("\nCustomer columns:")
    print(get_columns("customers"))    