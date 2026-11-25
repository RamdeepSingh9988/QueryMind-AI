
import os
import psycopg

from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

SQL_FILE = (
    Path(__file__).resolve().parent.parent
    / "sql"
    / "seed_orders.sql"
)


def seed_orders():

    sql = SQL_FILE.read_text()

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:

            cursor.execute("SELECT COUNT(*) FROM orders;")

            if cursor.fetchone()[0] > 0:
                print("Orders already exist. Skipping.")
                return

            cursor.execute(sql)

    print("Orders inserted successfully")


if __name__ == "__main__":
    seed_orders()
