
from backend.sql_validator import validate_sql


def test_valid_select():
    valid, message = validate_sql(
        "SELECT * FROM customers;"
    )

    assert valid is True


def test_delete_rejected():
    valid, message = validate_sql(
        "DELETE FROM customers;"
    )

    assert valid is False


def test_multiple_statements_rejected():
    valid, message = validate_sql(
        "SELECT * FROM customers; DELETE FROM customers;"
    )

    assert valid is False


def test_lock_rejected():
    valid, message = validate_sql(
        "SELECT * FROM customers FOR UPDATE;"
    )

    assert valid is False


def test_select_into_rejected():
    valid, message = validate_sql(
        "SELECT * INTO TEMP TABLE backup FROM customers;"
    )

    assert valid is False


def test_allowed_function():
    valid, message = validate_sql(
        "SELECT COUNT(*) FROM customers;"
    )

    assert valid is True



def test_empty_sql_rejected():
    valid, message = validate_sql("")

    assert valid is False


 
def test_unsafe_function_rejected():
    valid, message = validate_sql(
        "SELECT pg_sleep(10);"
    )

    assert valid is False
    assert "PG_SLEEP" in message 



def test_nested_delete_rejected():
    sql = """
    WITH deleted_customers AS (
        DELETE FROM customers
        RETURNING id
    )
    SELECT * FROM deleted_customers;
    """

    valid, message = validate_sql(sql)

    assert valid is False


def test_nested_update_rejected():
    sql = """
    WITH updated_customers AS (
        UPDATE customers
        SET name = 'Changed'
        RETURNING id
    )
    SELECT * FROM updated_customers;
    """

    valid, message = validate_sql(sql)

    assert valid is False


def test_safe_cte_allowed():
    sql = """
    WITH customer_orders AS (
        SELECT customer_id, COUNT(*) AS total_orders
        FROM orders
        GROUP BY customer_id
    )
    SELECT * FROM customer_orders;
    """

    valid, message = validate_sql(sql)

    assert valid is True
    assert message == "AST validation passed"
    



def test_allowed_table():
    valid, message = validate_sql(
        "SELECT * FROM customers;"
    )
    assert valid is True


def test_forbidden_table():
    valid, message = validate_sql(
        "SELECT * FROM admin_credentials;"
    )
    assert valid is False


def test_allowed_join():
    valid, message = validate_sql(
        """
        SELECT c.name, o.id
        FROM customers c
        JOIN orders o ON c.id = o.customer_id;
        """
    )
    assert valid is True



def test_cte_with_forbidden_table():
    sql = """
    WITH secret_data AS (
        SELECT * FROM admin_credentials
    )
    SELECT * FROM secret_data;
    """

    valid, message = validate_sql(sql)

    assert valid is False


def test_cte_with_allowed_table():
    sql = """
    WITH customer_data AS (
        SELECT id, name FROM customers
    )
    SELECT * FROM customer_data;
    """

    valid, message = validate_sql(sql)

    assert valid is True



def test_allowed_schema():
    valid, message = validate_sql(
        "SELECT * FROM public.customers;"
    )

    assert valid is True


def test_forbidden_schema():
    valid, message = validate_sql(
        "SELECT * FROM private.customers;"
    )

    assert valid is False
    assert "Schema private" in message


def test_system_schema_rejected():
    valid, message = validate_sql(
        "SELECT * FROM pg_catalog.pg_tables;"
    )

    assert valid is False


