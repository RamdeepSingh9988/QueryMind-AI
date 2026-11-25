
import json

from backend.ai_service import client
from backend.schema_discovery import get_full_schema
from backend.sql_generator import SQLResponse


def correct_sql(
    question: str,
    failed_sql: str,
    error_type: str
) -> SQLResponse:

    schema = get_full_schema()

    context = {
        "question": question,
        "failed_sql": failed_sql,
        "error_type": error_type,
        "database_schema": schema
    }

    response = client.responses.parse(
        model="gpt-4.1-mini",
        instructions="""
        You are a PostgreSQL query correction expert.

        Analyze the failed SQL query and database error.

        Rules:
        - Preserve the original user's intention.
        - Use only tables and columns from the schema.
        - Generate only SELECT queries.
        - Never bypass security restrictions.
        - Never invent missing data.
        - If the requested data is unavailable,
          return cannot_answer.
        - If the question is ambiguous,
          return needs_clarification.
        - Otherwise, return the corrected SQL
          with status success.
        """,
        input=json.dumps(context),
        text_format=SQLResponse
    )

    return response.output_parsed


if __name__ == "__main__":

    result = correct_sql(
        question="Show me all customer phone numbers",
        failed_sql="SELECT phone_number FROM customers;",
        error_type="Undefined column"
    )

    print(result.model_dump())
