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

def get_database_schema():
    tables = get_tables()

    schema = {}

    for table in tables:
        columns = get_columns(table)

        schema[table] = columns

    return schema   



def get_foreign_keys():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is missing")

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table,
                    ccu.column_name AS foreign_column
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.constraint_schema = kcu.constraint_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON tc.constraint_name = ccu.constraint_name
                    AND tc.constraint_schema = ccu.constraint_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_schema = 'public';
            """)

            rows = cursor.fetchall()

            foreign_keys = []

            for row in rows:
                foreign_keys.append({
                    "table": row[0],
                    "column": row[1],
                    "references_table": row[2],
                    "references_column": row[3]
                })

            return foreign_keys


def get_full_schema():
    tables = get_database_schema()
    relationships = get_foreign_keys()

    return {
        "tables": tables,
        "relationships": relationships
    }        


if __name__ == "__main__":
    import json

    schema = get_full_schema()

    print(json.dumps(schema, indent=2))