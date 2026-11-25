
from backend.sql_executor import execute_sql


if __name__ == "__main__":

    queries = {
        "products": "SELECT id, name, price FROM products;",
        "orders": "SELECT id, customer_id FROM orders;"
    }

    for name, query in queries.items():
        print(f"\n{name}:")
        print(execute_sql(query))
