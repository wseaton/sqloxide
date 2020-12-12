import pytest

from sqloxide import parse_sql
import sqlparse
import json


TEST_SQL = """
    SELECT employee.first_name, employee.last_name,
        call.start_time, call.end_time, call_outcome.outcome_text
    FROM employee
    INNER JOIN call ON call.employee_id = employee.id
    INNER JOIN call_outcome ON call.call_outcome_id = call_outcome.id
    ORDER BY call.start_time ASC;
    """


def bench_parse_sql():
    return parse_sql(sql=TEST_SQL, dialect="ansi")


def bench_parse_sql_json():
    return json.loads(parse_sql(sql=TEST_SQL, dialect="ansi"))


def bench_sqlparser():
    return sqlparse.parse(TEST_SQL)[0]


def test_sqloxide_json(benchmark):
    benchmark(bench_parse_sql_json)


def test_sqloxide(benchmark):
    benchmark(bench_parse_sql)


def test_sqlparser(benchmark):
    benchmark(bench_sqlparser)

