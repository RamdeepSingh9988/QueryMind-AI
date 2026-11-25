import pytest
from backend.result_interpreter import InterpretationResponse
from unittest.mock import patch

from backend.orchestrator import process_question
from backend.sql_generator import SQLResponse

@pytest.fixture(autouse=True)
def mock_interpreter():

    with patch(
        "backend.orchestrator.interpret_results"
    ) as mock:

        mock.return_value = InterpretationResponse(
            summary="Test summary",
            insights=["Test insight"],
            chart_type="bar"
        )

        yield mock

@patch("backend.orchestrator.correct_sql")
@patch("backend.orchestrator.generate_sql")
def test_sql_self_correction(
    mock_generate,
    mock_correct
):

    # Simulate incorrect AI-generated SQL
    mock_generate.return_value = SQLResponse(
        status="success",
        sql="SELECT email_address FROM customers;",
        message=None
    )

    # Simulate AI correcting the SQL
    mock_correct.return_value = SQLResponse(
        status="success",
        sql="SELECT email FROM customers;",
        message=None
    )

    # Run the complete workflow
    result = process_question(
        "Show me all customer emails"
    )

    # Verify the result
    assert result["status"] == "success"
    assert result["retry_count"] == 1
    assert result["self_corrected"] is True

    assert result["original_sql"] == (
        "SELECT email_address FROM customers;"
    )

    assert result["sql"] == (
        "SELECT email FROM customers;"
    )

    assert result["row_count"] == 3

    mock_generate.assert_called_once()

    mock_correct.assert_called_once_with(
        question="Show me all customer emails",
        failed_sql="SELECT email_address FROM customers;",
        error_type="Undefined column"
    )



@patch("backend.orchestrator.correct_sql")
@patch("backend.orchestrator.generate_sql")
def test_success_without_retry(mock_generate, mock_correct):

    mock_generate.return_value = SQLResponse(
        status="success",
        sql="SELECT name FROM customers;",
        message=None
    )

    result = process_question("Show all customer names")

    assert result["status"] == "success"
    assert result["retry_count"] == 0
    assert result["self_corrected"] is False

    mock_correct.assert_not_called()



@patch("backend.orchestrator.correct_sql")
@patch("backend.orchestrator.generate_sql")
def test_security_violation(mock_generate, mock_correct):

    mock_generate.return_value = SQLResponse(
        status="success",
        sql="DELETE FROM customers;",
        message=None
    )

    result = process_question("Delete all customers")

    assert result["status"] == "rejected"
    assert result["retry_count"] == 0

    mock_correct.assert_not_called()



@patch("backend.orchestrator.correct_sql")
@patch("backend.orchestrator.generate_sql")
def test_failed_correction(mock_generate, mock_correct):

    mock_generate.return_value = SQLResponse(
        status="success",
        sql="SELECT email_address FROM customers;",
        message=None
    )

    mock_correct.return_value = SQLResponse(
        status="success",
        sql="SELECT customer_email FROM customers;",
        message=None
    )

    result = process_question("Show customer emails")

    assert result["status"] == "error"
    assert result["retry_count"] == 1
    assert result["self_corrected"] is False

    mock_correct.assert_called_once()



@patch("backend.orchestrator.correct_sql")
@patch("backend.orchestrator.generate_sql")
def test_cannot_answer(mock_generate, mock_correct):

    mock_generate.return_value = SQLResponse(
        status="success",
        sql="SELECT phone_number FROM customers;",
        message=None
    )

    mock_correct.return_value = SQLResponse(
        status="cannot_answer",
        sql=None,
        message="Customer phone numbers are unavailable."
    )

    result = process_question("Show customer phone numbers")

    assert result["status"] == "cannot_answer"
    assert result["data"] == []
    assert result["retry_count"] == 1

    mock_correct.assert_called_once()



@patch("backend.orchestrator.correct_sql")
@patch("backend.orchestrator.execute_sql")
@patch("backend.orchestrator.generate_sql")
def test_permission_error(
    mock_generate,
    mock_execute,
    mock_correct
):

    mock_generate.return_value = SQLResponse(
        status="success",
        sql="SELECT name FROM customers;",
        message=None
    )

    mock_execute.return_value = {
        "status": "error",
        "message": "Database query failed",
        "error_code": "42501",
        "error_type": "Database error",
        "retryable": False,
        "data": []
    }

    result = process_question("Show customer names")

    assert result["status"] == "error"
    assert result["retry_count"] == 0

    mock_correct.assert_not_called()
    mock_execute.assert_called_once()



@patch("backend.orchestrator.generate_sql")
def test_result_interpretation(
    mock_generate,
    mock_interpreter
):

    mock_generate.return_value = SQLResponse(
        status="success",
        sql="SELECT name FROM customers;",
        message=None
    )

    result = process_question(
        "Show all customer names"
    )

    assert result["status"] == "success"

    assert result["interpretation_status"] == "success"

    assert result["interpretation"]["summary"] == (
        "Test summary"
    )

    assert result["interpretation"]["chart_type"] == "bar"

    mock_interpreter.assert_called_once()



@patch("backend.orchestrator.generate_sql")
def test_interpretation_failure(
    mock_generate,
    mock_interpreter
):

    mock_generate.return_value = SQLResponse(
        status="success",
        sql="SELECT name FROM customers;",
        message=None
    )

    mock_interpreter.side_effect = Exception(
        "AI service unavailable"
    )

    result = process_question(
        "Show all customer names"
    )

    assert result["status"] == "success"

    assert result["row_count"] == 3

    assert result["interpretation"] is None

    assert result["interpretation_status"] == "error"

    mock_interpreter.assert_called_once()
