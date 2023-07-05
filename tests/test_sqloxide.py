import pytest
from sqloxide import (
    parse_sql,
    restore_ast,
    extract_relations,
    mutate_relations,
    extract_expressions,
    mutate_expressions,
)


SQL = """
    SELECT employee.first_name, employee.last_name,
    c.start_time, c.end_time, call_outcome.outcome_text
    FROM employee
    INNER JOIN "call"."call"."call" c ON c.employee_id = employee.id
    INNER JOIN call_outcome ON c.call_outcome_id = call_outcome.id
    ORDER BY c.start_time ASC;
"""


def test_parse_sql():
    ast = parse_sql(sql=SQL, dialect="ansi")[0]

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
    ast = parse_sql(sql=SQL, dialect="ansi")

    assert extract_relations(parsed_query=ast)[0][0] == {
        "value": "employee",
        "quote_style": None,
    }


def test_mutate_relations():
    def func(x):
        return x.replace("call", "call2")

    ast = parse_sql(sql=SQL, dialect="ansi")
    assert mutate_relations(parsed_query=ast, func=func) == [
        'SELECT employee.first_name, employee.last_name, c.start_time, c.end_time, call_outcome.outcome_text FROM employee JOIN "call2"."call2"."call2" AS c ON c.employee_id = employee.id JOIN call2_outcome ON c.call_outcome_id = call_outcome.id ORDER BY c.start_time ASC'
    ]


def test_restore_ast():
    """
    Note, we are stripping formatting from the SQL string before comparing because
    formatting is not expected to be preserved.
    """
    sql = "SELECT employee.first_name, employee.last_name, call.start_time, call.end_time, call_outcome.outcome_text FROM employee JOIN call ON call.employee_id = employee.id JOIN call_outcome ON call.call_outcome_id = call_outcome.id ORDER BY call.start_time ASC"

    ast = parse_sql(sql=sql, dialect="ansi")
    print(ast)
    # testing that the query roundtrips
    assert sql == restore_ast(ast=ast)[0]


def test_mutate_expressions():
    def func(x):
        if "CompoundIdentifier" in x.keys():
            for y in x["CompoundIdentifier"]:
                y["value"] = y["value"].upper()
        return x

    ast = parse_sql(sql=SQL, dialect="ansi")
    result = mutate_expressions(parsed_query=ast, func=func)
    assert result == [
        'SELECT EMPLOYEE.FIRST_NAME, EMPLOYEE.LAST_NAME, C.START_TIME, C.END_TIME, CALL_OUTCOME.OUTCOME_TEXT FROM employee JOIN "call"."call"."call" AS c ON C.EMPLOYEE_ID = EMPLOYEE.ID JOIN call_outcome ON C.CALL_OUTCOME_ID = CALL_OUTCOME.ID ORDER BY C.START_TIME ASC'
    ]


def test_extract_expressions():
    ast = parse_sql(sql=SQL, dialect="ansi")
    exprs = extract_expressions(parsed_query=ast)
    for expr in exprs:
        print("EXPR: ", expr)

    assert exprs[0] == {
        "CompoundIdentifier": [
            {"value": "employee", "quote_style": None},
            {"value": "first_name", "quote_style": None},
        ]
    }
