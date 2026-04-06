"""Validate that actual pythonize output matches the type stubs in sqloxide/__init__.pyi.

We parse a diverse set of SQL statements and structurally verify the output
against the TypedDict shapes declared in our stubs. This catches drift between
sqlparser-rs serde output and our hand-written types.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqloxide import parse_sql

if TYPE_CHECKING:
    from sqloxide import Dialect

# Diverse queries covering major statement types, sourced from sqlparser-rs tests
SQL_TEST_QUERIES: list[tuple[str, Dialect]] = [
    # SELECT variants
    ("SELECT id, fname, lname FROM customer WHERE id = 1 LIMIT 5", "generic"),
    ("SELECT a.col + 1 AS newname FROM foo AS a", "generic"),
    ("SELECT COUNT(*), department FROM employees GROUP BY department HAVING COUNT(*) > 5", "generic"),
    ("SELECT DISTINCT name FROM customer", "generic"),
    ("SELECT * FROM foo WHERE id IN (SELECT id FROM bar WHERE active = 1)", "generic"),
    ("SELECT * FROM t1 LEFT JOIN t2 ON t1.id = t2.t1_id INNER JOIN t3 ON t1.id = t3.t1_id", "generic"),
    ("WITH cte (col1, col2) AS (SELECT foo, bar FROM baz) SELECT * FROM cte", "generic"),
    ("SELECT column1, FIRST_VALUE(column2) OVER (PARTITION BY column1 ORDER BY column2 NULLS LAST) FROM t1", "generic"),
    ("SELECT 1 UNION SELECT 2", "generic"),
    # INSERT
    ("INSERT INTO customer VALUES (1, 2, 3)", "generic"),
    ("INSERT INTO public.customer (id, name, active) VALUES (1, 2, 3)", "generic"),
    # UPDATE
    ("UPDATE t SET a = 1, b = 2, c = 3 WHERE d", "generic"),
    # DELETE
    ("DELETE FROM foo WHERE name = 5", "generic"),
    # DDL
    ("CREATE TABLE IF NOT EXISTS t (id INT NOT NULL, name VARCHAR(100), PRIMARY KEY (id))", "generic"),
    ("CREATE TABLE t AS SELECT * FROM a", "generic"),
    ("CREATE VIEW myschema.myview AS SELECT foo FROM bar", "generic"),
    ("DROP TABLE IF EXISTS foo, bar CASCADE", "generic"),
    ("ALTER TABLE tab ADD COLUMN foo TEXT", "generic"),
    # DCL
    ("GRANT SELECT, INSERT ON abc TO xyz WITH GRANT OPTION", "generic"),
    ("REVOKE ALL PRIVILEGES ON users, auth FROM analyst CASCADE", "generic"),
    # DML
    ("TRUNCATE TABLE employee", "generic"),
    ("SET TIMEZONE = 'UTC'", "generic"),
]

# Expected fields per struct, derived from our stubs
QUERY_FIELDS = {"with", "body", "order_by", "limit_clause", "fetch", "locks", "for_clause", "settings", "format_clause", "pipe_operators"}
SELECT_FIELDS = {
    "select_token", "optimizer_hint", "distinct", "select_modifiers", "top",
    "top_before_distinct", "projection", "exclude", "into", "from",
    "lateral_views", "prewhere", "selection", "connect_by", "group_by",
    "cluster_by", "distribute_by", "sort_by", "having", "named_window",
    "qualify", "window_before_qualify", "value_table_mode", "flavor",
}
IDENT_FIELDS = {"value", "quote_style", "span"}
SPAN_FIELDS = {"start", "end"}
SOURCE_LOCATION_FIELDS = {"line", "column"}
TABLE_FIELDS = {"name", "alias", "args", "with_hints", "version", "with_ordinality", "partitions", "json_path", "sample", "index_hints"}
TABLE_WITH_JOINS_FIELDS = {"relation", "joins"}


def validate_ident(ident: dict) -> None:
    assert IDENT_FIELDS.issubset(ident.keys()), f"Ident missing fields: {IDENT_FIELDS - ident.keys()}, got {set(ident.keys())}"
    assert isinstance(ident["value"], str)
    assert ident["quote_style"] is None or isinstance(ident["quote_style"], str)

    span = ident["span"]
    assert SPAN_FIELDS.issubset(span.keys()), f"Span missing fields: {SPAN_FIELDS - span.keys()}"
    for loc_key in ("start", "end"):
        loc = span[loc_key]
        assert SOURCE_LOCATION_FIELDS.issubset(loc.keys()), f"SourceLocation missing: {SOURCE_LOCATION_FIELDS - loc.keys()}"
        assert isinstance(loc["line"], int)
        assert isinstance(loc["column"], int)


def validate_object_name_part(part: dict) -> None:
    assert "Identifier" in part or "Function" in part, f"ObjectNamePart has unexpected key: {set(part.keys())}"
    if "Identifier" in part:
        validate_ident(part["Identifier"])


def validate_object_name(name: list) -> None:
    assert isinstance(name, list)
    assert len(name) > 0
    for part in name:
        validate_object_name_part(part)


def validate_table(table: dict) -> None:
    assert TABLE_FIELDS.issubset(table.keys()), f"Table missing fields: {TABLE_FIELDS - table.keys()}, got {set(table.keys())}"
    validate_object_name(table["name"])
    assert isinstance(table["with_hints"], list)
    assert isinstance(table["partitions"], list)
    assert isinstance(table["with_ordinality"], bool)


def validate_table_with_joins(twj: dict) -> None:
    assert TABLE_WITH_JOINS_FIELDS.issubset(twj.keys()), f"TableWithJoins missing fields: {TABLE_WITH_JOINS_FIELDS - twj.keys()}"
    assert isinstance(twj["joins"], list)
    relation = twj["relation"]
    assert isinstance(relation, dict)
    if "Table" in relation:
        validate_table(relation["Table"])


def validate_select(select: dict) -> None:
    assert SELECT_FIELDS.issubset(select.keys()), f"Select missing fields: {SELECT_FIELDS - select.keys()}, got {set(select.keys())}"
    assert isinstance(select["projection"], list)
    assert isinstance(select["from"], list)
    assert isinstance(select["top_before_distinct"], bool)
    assert isinstance(select["window_before_qualify"], bool)
    assert isinstance(select["lateral_views"], list)
    assert isinstance(select["cluster_by"], list)
    assert isinstance(select["distribute_by"], list)
    assert isinstance(select["sort_by"], list)
    assert isinstance(select["named_window"], list)

    for twj in select["from"]:
        validate_table_with_joins(twj)


def validate_query(query: dict) -> None:
    assert QUERY_FIELDS.issubset(query.keys()), f"Query missing fields: {QUERY_FIELDS - query.keys()}, got {set(query.keys())}"
    assert isinstance(query["locks"], list)
    assert isinstance(query["pipe_operators"], list)

    body = query["body"]
    assert isinstance(body, dict)
    if "Select" in body:
        validate_select(body["Select"])


def test_all_queries_parse():
    """Every test query should parse without error."""
    for sql, dialect in SQL_TEST_QUERIES:
        result = parse_sql(sql=sql, dialect=dialect)
        assert isinstance(result, list), f"Expected list, got {type(result)} for: {sql}"
        assert len(result) > 0, f"Empty result for: {sql}"


def test_select_structure():
    """Validate the full Query > Select > Table path for SELECT statements."""
    select_queries = [
        (sql, dialect) for sql, dialect in SQL_TEST_QUERIES
        if sql.strip().upper().startswith("SELECT") or sql.strip().upper().startswith("WITH")
    ]
    assert len(select_queries) > 0

    for sql, dialect in select_queries:
        result = parse_sql(sql=sql, dialect=dialect)
        stmt = result[0]
        assert "Query" in stmt, f"Expected Query wrapper, got {set(stmt.keys())} for: {sql}"
        validate_query(stmt["Query"])


def test_insert_structure():
    """Validate Insert statement structure."""
    insert_fields = {"insert_token", "ignore", "into", "columns", "overwrite", "has_table_keyword", "replace_into"}

    for sql, dialect in SQL_TEST_QUERIES:
        if not sql.strip().upper().startswith("INSERT"):
            continue
        result = parse_sql(sql=sql, dialect=dialect)
        stmt = result[0]
        assert "Insert" in stmt, f"Expected Insert wrapper, got {set(stmt.keys())} for: {sql}"
        insert = stmt["Insert"]
        assert insert_fields.issubset(insert.keys()), f"Insert missing fields: {insert_fields - insert.keys()}"
        assert isinstance(insert["columns"], list)
        assert isinstance(insert["ignore"], bool)
        assert isinstance(insert["into"], bool)
        assert isinstance(insert["overwrite"], bool)
        assert isinstance(insert["has_table_keyword"], bool)
        assert isinstance(insert["replace_into"], bool)


def test_update_structure():
    """Validate Update statement structure."""
    for sql, dialect in SQL_TEST_QUERIES:
        if not sql.strip().upper().startswith("UPDATE"):
            continue
        result = parse_sql(sql=sql, dialect=dialect)
        stmt = result[0]
        assert "Update" in stmt, f"Expected Update wrapper, got {set(stmt.keys())} for: {sql}"
        update = stmt["Update"]
        assert "assignments" in update
        assert isinstance(update["assignments"], list)
        assert "table" in update


def test_delete_structure():
    """Validate Delete statement structure."""
    for sql, dialect in SQL_TEST_QUERIES:
        if not sql.strip().upper().startswith("DELETE"):
            continue
        result = parse_sql(sql=sql, dialect=dialect)
        stmt = result[0]
        assert "Delete" in stmt, f"Expected Delete wrapper, got {set(stmt.keys())} for: {sql}"
        delete = stmt["Delete"]
        assert "from" in delete or "from_" in delete or "tables" in delete


def test_ident_shape():
    """Every Identifier in the AST should have value, quote_style, span."""
    result = parse_sql(sql="SELECT foo, bar FROM baz", dialect="generic")
    query = result[0]["Query"]
    select = query["body"]["Select"]

    for proj in select["projection"]:
        if "UnnamedExpr" in proj:
            expr = proj["UnnamedExpr"]
            if "Identifier" in expr:
                validate_ident(expr["Identifier"])

    for twj in select["from"]:
        if "Table" in twj["relation"]:
            table = twj["relation"]["Table"]
            for part in table["name"]:
                validate_object_name_part(part)


def test_table_alias_has_explicit():
    """TableAlias gained an `explicit` bool in sqlparser 0.60."""
    result = parse_sql(sql="SELECT * FROM foo AS f", dialect="generic")
    table = result[0]["Query"]["body"]["Select"]["from"][0]["relation"]["Table"]
    alias = table["alias"]
    assert alias is not None
    assert "explicit" in alias, f"TableAlias missing 'explicit' field, got {set(alias.keys())}"
    assert isinstance(alias["explicit"], bool)
    assert alias["explicit"] is True  # AS keyword was present

    result2 = parse_sql(sql="SELECT * FROM foo f", dialect="generic")
    table2 = result2[0]["Query"]["body"]["Select"]["from"][0]["relation"]["Table"]
    alias2 = table2["alias"]
    assert alias2 is not None
    assert alias2["explicit"] is False  # no AS keyword
