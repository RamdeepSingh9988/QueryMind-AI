
import os
import psycopg

from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

SQL_FILE = (
    Path(__file__).resolve().parent.parent
    / "sql"
    / "seed_order_items.sql"
)


def seed_order_items():

    sql = SQL_FILE.read_text()

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                "SELECT COUNT(*) FROM order_items;"
            )

            if cursor.fetchone()[0] > 0:
                print("Order items already exist. Skipping.")
                return

            cursor.execute(sql)

    print("Order items inserted successfully")


if __name__ == "__main__":
    seed_order_items()
