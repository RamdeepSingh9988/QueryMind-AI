
import sqlglot
from sqlglot import exp

queries = [
    "SELECT COUNT(*) FROM customers;",
    "SELECT SUM(quantity) FROM order_items;",
    "SELECT pg_sleep(10);",
]

for sql in queries:
    statement = sqlglot.parse_one(
        sql,
        read="postgres"
    )

    print("\nSQL:", repr(sql))

    for function in statement.find_all(exp.Func):
        print("Function:", function.sql_name())
        print("Expression type:", type(function).__name__)
