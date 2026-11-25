
from backend.sql_generator import generate_sql
from backend.sql_executor import execute_sql
from backend.sql_corrector import correct_sql


def process_question(question: str) -> dict:

    # Step 1: Generate SQL
    ai_response = generate_sql(question)

    if ai_response.status != "success":
        return {
            "status": ai_response.status,
            "question": question,
            "message": ai_response.message,
            "sql": None,
            "data": []
        }

    if not ai_response.sql:
        return {
            "status": "error",
            "message": "AI did not generate SQL",
            "data": []
        }

    # Step 2: Execute initial SQL
    result = execute_sql(ai_response.sql)

    # Step 3: Check if correction is needed
    if (
        result["status"] == "error"
        and result.get("retryable", False)
    ):

        # Step 4: Ask AI to correct SQL
        corrected = correct_sql(
            question=question,
            failed_sql=ai_response.sql,
            error_type=result["error_type"]
        )

        # Step 5: Check correction response
        if corrected.status != "success":
            return {
                "status": corrected.status,
                "question": question,
                "message": corrected.message,
                "sql": None,
                "data": [],
                "retry_count": 1
            }

        if not corrected.sql:
            return {
                "status": "error",
                "message": "SQL correction failed",
                "data": [],
                "retry_count": 1
            }

        # Step 6: Validate and execute corrected SQL
        corrected_result = execute_sql(corrected.sql)

        return {
            "question": question,
            "original_sql": ai_response.sql,
            "sql": corrected.sql,
            "retry_count": 1,
            "self_corrected": (
                corrected_result["status"] == "success"
            ),
            **corrected_result
        }

    # Step 7: Return initial result
    return {
        "question": question,
        "sql": ai_response.sql,
        "retry_count": 0,
        "self_corrected": False,
        **result
    }


if __name__ == "__main__":

    result = process_question(
        "Show me all customer names"
    )

    print(result)