
from backend.sql_generator import generate_sql
from backend.sql_executor import execute_sql
from backend.sql_corrector import correct_sql
from backend.result_interpreter import interpret_results


def enrich_result(result: dict) -> dict:

    if result["status"] != "success":
        return result

    try:
        interpretation = interpret_results(
            question=result["question"],
            sql=result["sql"],
            data=result["data"],
            truncated=result.get("truncated", False)
        )

        return {
            **result,
            "interpretation": interpretation.model_dump(),
            "interpretation_status": "success"
        }

    except Exception:
        return {
            **result,
            "interpretation": None,
            "interpretation_status": "error"
        }



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

        return enrich_result({
        "question": question,
        "original_sql": ai_response.sql,
        "sql": corrected.sql,
        "retry_count": 1,
        "self_corrected": (
            corrected_result["status"] == "success"
        ),
        **corrected_result
        })

    # Step 7: Return initial result
    return enrich_result ({
        "question": question,
        "sql": ai_response.sql,
        "retry_count": 0,
        "self_corrected": False,
        **result
    })



if __name__ == "__main__":

    import json

    result = process_question(
        "Show total revenue for each product, "
        "calculated as quantity multiplied by unit_price, "
        "sorted from highest to lowest total revenue."
    )

    print(json.dumps(result, indent=2, default=str))