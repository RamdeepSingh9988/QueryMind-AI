import os
import psycopg

from dotenv import load_dotenv
from psycopg.rows import dict_row
from backend.sql_validator import validate_sql

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

MAX_ROWS = 100
QUERY_TIMEOUT_MS = 5000


def execute_sql(sql: str) -> dict:

    valid, message = validate_sql(sql)

    if not valid:
        return {
            "status": "rejected",
            "message": message,
            "data": []
        }

    try:
        with psycopg.connect(
            DATABASE_URL,
            row_factory=dict_row,
            connect_timeout=5
        ) as conn:

            conn.read_only = True

            with conn.cursor() as cursor:

                cursor.execute(
                    f"SET LOCAL statement_timeout = {QUERY_TIMEOUT_MS}"
                )

                cursor.execute(
                    "SET LOCAL search_path = pg_catalog, public, pg_temp"
                )

                cursor.execute(sql)

                rows = cursor.fetchmany(MAX_ROWS + 1)

                return {
                    "status": "success",
                    "message": "Query executed successfully",
                    "data": rows[:MAX_ROWS],
                    "row_count": min(len(rows), MAX_ROWS),
                    "truncated": len(rows) > MAX_ROWS
                }

   
    except psycopg.Error as error:

        error_code = error.sqlstate

        recoverable_errors = {
            "42703": "Undefined column",
            "42P01": "Undefined table",
            "42601": "SQL syntax error",
            "42803": "Grouping error",
            "42883": "Undefined function",
        }

        return {
            "status": "error",
            "message": "Database query failed",
            "error_code": error_code,
            "error_type": recoverable_errors.get(
                error_code,
                "Database error"
            ),
            "retryable": error_code in recoverable_errors,
            "data": []
        }



if __name__ == "__main__":

    queries = [
        "SELECT name FROM customers;",
        "SELECT phone_number FROM customers;",
        "DELETE FROM customers;",
    ]

    for query in queries:
        print("\nSQL:", query)
        print(execute_sql(query))