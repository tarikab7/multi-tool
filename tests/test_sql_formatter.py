import pytest
from tools.sql_formatter import run

@pytest.mark.asyncio
async def test_sql_formatter_run_missing_params():
    # Pass an empty dict, which should yield the error dictionary
    results = [res async for res in run({})]
    assert len(results) == 1
    assert results[0] == {"type": "error", "message": "SQL query string is required."}

@pytest.mark.asyncio
async def test_sql_formatter_run_success():
    # Happy path: test a valid SQL statement
    sql_input = "SELECT * FROM users WHERE age > 20"
    params = {"sql": sql_input}

    results = [res async for res in run(params)]

    # We expect log, found, and success yields
    assert len(results) == 3
    assert results[0] == {"type": "log", "message": "Running syntax formatter on SQL statement..."}
    assert results[1]["type"] == "found"
    # Basic check to see if formatting did something like adding newlines around FROM, WHERE
    assert "SELECT" in results[1]["message"]
    assert "FROM" in results[1]["message"]
    assert "WHERE" in results[1]["message"]
    assert results[2] == {"type": "success", "message": "SQL formatted successfully."}
