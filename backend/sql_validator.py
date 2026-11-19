
def validate_sql(sql):
    sql = sql.strip()

    if not sql:
        return False, "SQL query is empty"

    if not sql.upper().startswith("SELECT"):
        return False, "Only SELECT queries are allowed"

    return True, "Basic validation passed"


if __name__ == "__main__":
    queries = [
        "SELECT * FROM customers;",
        "DELETE FROM customers;",
        "",
    ]

    for query in queries:
        valid, message = validate_sql(query)

        print("SQL:", repr(query))
        print("Valid:", valid)
        print("Message:", message)
        print("---")
