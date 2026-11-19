
import os

import psycopg
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is missing")

with psycopg.connect(database_url) as conn:
    with conn.cursor() as cursor:

        cursor.execute("SELECT * FROM customers;")

        customers = cursor.fetchall()

        for customer in customers:
            print(customer)
