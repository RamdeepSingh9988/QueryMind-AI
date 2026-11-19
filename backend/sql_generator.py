
import json

from backend.schema_discovery import get_full_schema
from backend.ai_service import client
from typing import Literal
from pydantic import BaseModel


class SQLResponse(BaseModel):
    # restricts the value to exactly those three options using Literal from typing
    status: Literal[
        "success",
        "needs_clarification",
        "cannot_answer"
    ]
    sql: str | None
    message: str | None

def generate_sql(question):
    schema = get_full_schema()

    schema_text = json.dumps(schema, indent=2)

    response = client.responses.parse(
        model="gpt-4.1-mini",
        instructions="""
       
        You are a PostgreSQL SQL generator and question analyst.

        Your first task is to determine whether the user's
        question is clear and answerable.

        Follow this decision order:

        1. MISSING DATA
        If the user requests information that does not exist
        in the database schema:
        - status = "cannot_answer"
        - sql = null
        - Explain which information is missing.

        2. AMBIGUOUS QUESTION
        If the question has multiple reasonable interpretations
        that could produce different SQL results:
        - status = "needs_clarification"
        - sql = null
        - Ask one specific clarification question.

        Examples:
        - "Most popular product" could mean most units sold
            or most distinct orders.
        - "Best customer" could mean highest spending
            or most orders.
        - "Top products" could mean highest revenue
            or highest quantity sold.

        Do not silently choose a metric when the user
        has not specified one.

        3. CLEAR QUESTION
        If the question is clear and answerable:
        - status = "success"
        - Generate PostgreSQL SELECT SQL.
        - message = null

        SQL RULES:
        - Use only existing tables and columns.
        - Use foreign-key relationships for joins.
        - Generate only SELECT queries.
        - Never invent database fields.
        - Never generate INSERT, UPDATE, DELETE, DROP,
        ALTER, or TRUNCATE statements.
        """,
        input=f"""
        Database schema:
        {schema_text}

        User question:
        {question}
        """,
        text_format=SQLResponse
    )

    return response.output_parsed


if __name__ == "__main__":
    question = "Show me the most popular product."

    result = generate_sql(question)

    print("\nStatus:", result.status)
    print("SQL:", result.sql)
    print("Message:", result.message)
