
from backend.sql_generator import generate_sql
from backend.sql_executor import execute_sql


def process_question(question: str) -> dict:

    # Step 1: Generate SQL using AI
    ai_response = generate_sql(question)

    # Step 2: Check the AI decision
    if ai_response.status != "success":
        return {
            "status": ai_response.status,
            "question": question,
            "message": ai_response.message,
            "sql": None,
            "data": []
        }

    # Step 3: Ensure SQL exists
    if not ai_response.sql:
        return {
            "status": "error",
            "message": "AI did not generate SQL",
            "data": []
        }

    # Step 4: Validate and execute SQL
    result = execute_sql(ai_response.sql)

    # Step 5: Return combined response
    return {
        "question": question,
        "sql": ai_response.sql,
        **result
    }

if __name__ == "__main__":

    result = process_question(
        "Show me all customer names"
    )

    print(result)