import pytest
from sqloxide import parse_sql, extract_relations, mutate_relations, restore_ast


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
    with pytest.raises(
        ValueError, match=r"Query parsing failed.\n\tsql parser error: .+"
    ):
        _ast = parse_sql(sql=sql, dialect="ansi")[0]


def test_extract_relations():
    sql = """
    SELECT employee.first_name, employee.last_name,
        call.start_time, call.end_time, call_outcome.outcome_text
    FROM employee
    INNER JOIN call ON call.employee_id = employee.id
    INNER JOIN call_outcome ON call.call_outcome_id = call_outcome.id
    ORDER BY call.start_time ASC;
    """

    ast = parse_sql(sql=sql, dialect="ansi")
    print(extract_relations(parsed_query=ast))


def test_mutate_relations():
    sql = """
    SELECT employee.first_name, employee.last_name,
        c.start_time, c.end_time, call_outcome.outcome_text
    FROM employee
    INNER JOIN "call"."call"."call" c ON c.employee_id = employee.id
    INNER JOIN call_outcome ON c.call_outcome_id = call_outcome.id
    ORDER BY c.start_time ASC;
    """

    def func(x):
        return x.replace("call", "call2")

    ast = parse_sql(sql=sql, dialect="ansi")
    print(mutate_relations(parsed_query=ast, func=func))


def test_restore_ast():
    """
    Note, we are stripping formatting from the SQL string before comparing because
    formatting is not expected to be preserved.
    """
    sql = "SELECT employee.first_name, employee.last_name, call.start_time, call.end_time, call_outcome.outcome_text FROM employee JOIN call ON call.employee_id = employee.id JOIN call_outcome ON call.call_outcome_id = call_outcome.id ORDER BY call.start_time ASC"

    ast = parse_sql(sql=sql, dialect="ansi")
    # testing that the query roundtrips
    assert sql == restore_ast(ast=ast)[0]
