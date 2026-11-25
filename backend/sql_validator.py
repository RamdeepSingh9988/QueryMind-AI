
import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError
from sqlglot.optimizer.scope import traverse_scope

ALLOWED_FUNCTIONS = {
    "COUNT",
    "SUM",
    "AVG",
    "MIN",
    "MAX",
}
FORBIDDEN_OPERATIONS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Create,
    exp.Drop,
    exp.Alter,
    exp.Merge,
    exp.Command,
)

ALLOWED_TABLES = {
    "customers",
    "orders",
    "products",
    "order_items",
}
ALLOWED_SCHEMAS = {"public"}

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

    for node in statement.walk():
        if isinstance(node, FORBIDDEN_OPERATIONS):
            return False, (
                f"Forbidden SQL operation: "
                f"{type(node).__name__}"
            )

    
    for function in statement.find_all(exp.Func):
        if isinstance(function, exp.Anonymous):
            function_name = function.name.upper()
        else:
            function_name = function.sql_name().upper()

        if function_name not in ALLOWED_FUNCTIONS:
            return False, f"Function {function_name} is not allowed"


    
    # Validate real database tables across query scopes

    # Validate database tables and schemas
    try:
        scopes = traverse_scope(statement)

        if not scopes:
            return False, "Unable to analyze SQL scopes"

        for scope in scopes:
            for _, source in scope.selected_sources.values():

                if isinstance(source, exp.Table):
                    table_name = source.name
                    schema_name = source.db or "public"

                    if source.catalog:
                        return False, "Catalog access is not allowed"

                    if schema_name not in ALLOWED_SCHEMAS:
                        return False, (
                            f"Schema {schema_name} is not allowed"
                        )

                    if table_name not in ALLOWED_TABLES:
                        return False, (
                            f"Table {table_name} is not allowed"
                        )

    except Exception:
        return False, "SQL scope analysis failed"

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
