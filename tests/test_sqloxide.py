import pytest
from sqloxide import parse_sql


def test_parse_sql():

    sql = """
    SELECT employee.first_name, employee.last_name,
        call.start_time, call.end_time, call_outcome.outcome_text
    FROM employee
    INNER JOIN call ON call.employee_id = employee.id
    INNER JOIN call_outcome ON call.call_outcome_id = call_outcome.id
    ORDER BY call.start_time ASC;
    """

    ast = parse_sql(sql=sql, dialect="ansi")[0]

    assert isinstance(ast, dict)
    assert len(ast["Query"].keys()) > 0

    assert "order_by" in ast["Query"].keys()
    assert "body" in ast["Query"].keys()


def test_throw_exception():

    sql = """
    SELECT $# as 1;
    """
    with pytest.raises(ValueError, match=r"Query parsing failed.\n\tsql parser error: .+"):
        ast = parse_sql(sql=sql, dialect="ansi")[0]
