
import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError

ALLOWED_FUNCTIONS = {
    "COUNT",
    "SUM",
    "AVG",
    "MIN",
    "MAX",
}

def validate_sql(sql):
    if not sql or not sql.strip():
        return False, "SQL query is empty"

    try:
        statements = sqlglot.parse(
            sql,
            read="postgres"
        )
    except ParseError as error:
        return False, f"SQL parsing failed: {error}"

    statements = [
        statement
        for statement in statements
        if statement is not None
    ]

    if len(statements) != 1:
        return False, "Only one SQL statement is allowed"

    statement = statements[0]


    if not isinstance(statement, exp.Select):
        return False, "Only SELECT queries are allowed"

    # Reject row-locking operations
    if statement.find(exp.Lock):
        return False, "Locking operations are not allowed"

    # Reject SELECT INTO, which can create tables
    if statement.find(exp.Into):
        return False, "SELECT INTO is not allowed"

    
    for function in statement.find_all(exp.Func):
        if isinstance(function, exp.Anonymous):
            function_name = function.name.upper()
        else:
            function_name = function.sql_name().upper()

        if function_name not in ALLOWED_FUNCTIONS:
            return False, f"Function {function_name} is not allowed"


    return True, "AST validation passed"



if __name__ == "__main__":
    queries = [
      "SELECT COUNT(*) FROM customers;",
        "SELECT SUM(quantity) FROM order_items;",
        "SELECT AVG(price) FROM products;",
        "SELECT pg_sleep(10);",
        "SELECT * FROM customers;",
        "",
    ]

    for query in queries:
        valid, message = validate_sql(query)

        print("SQL:", repr(query))
        print("Valid:", valid)
        print("Message:", message)
        print("---")
