
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# Step 1: Load environment variables
load_dotenv()

# Step 2: Get database connection URL
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is missing")

# Step 3: Find our SQL file
sql_file = (
    Path(__file__).resolve().parent.parent
    / "sql"
    / "seed.sql"
)

# Step 4: Read SQL from the file
sql = sql_file.read_text()

# Step 5: Connect and execute
with psycopg.connect(database_url) as conn:
    with conn.cursor() as cursor:
        cursor.execute(sql)

print("Sample data inserted successfully!")
