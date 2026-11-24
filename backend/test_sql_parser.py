
import sqlglot
from sqlglot import exp

sql = """
WITH deleted_customers AS (
    DELETE FROM customers
    RETURNING id
)
SELECT * FROM deleted_customers;
"""

statement = sqlglot.parse_one(
    sql,
    read="postgres"
)

print("Outer statement:", type(statement).__name__)

for node in statement.walk():
    print(type(node).__name__)



    
