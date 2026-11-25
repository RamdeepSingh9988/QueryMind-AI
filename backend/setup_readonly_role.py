
import os
import psycopg

from dotenv import load_dotenv
from getpass import getpass
from psycopg import sql

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def create_readonly_role():
    password = getpass("Enter password for querymind_reader: ")

    if not password:
        raise ValueError("Password cannot be empty")

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:

            query = sql.SQL("""
                CREATE ROLE querymind_reader
                WITH LOGIN PASSWORD {}
            """).format(sql.Literal(password))

            cursor.execute(query)

    print("Database role created successfully")


if __name__ == "__main__":
    create_readonly_role()
