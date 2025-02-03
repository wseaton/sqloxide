from typing import Any, Generic, Literal, TypeAlias, TypedDict, TypeVar

Dialect: TypeAlias = Literal["generic", "ansi", "sqlite", "postgresql"]

def parse_sql(sql: str, dialect: Dialect) -> list[Statement]: ...

T = TypeVar("T")

ObjectName: TypeAlias = list[Ident]
"""
A name of a table, view, custom type, etc.
(possibly multi-part, i.e. db.schema.obj)
"""

Statement: TypeAlias = AstSelect | AstInsert | AstSetVariable | dict[str, Any]
"""
A top-level statement (SELECT, INSERT, CREATE, etc.)

See https://docs.rs/sqlparser/0.51.0/sqlparser/ast/enum.Statement.html
"""

SetExpr: TypeAlias = AstSelect | AstSelect | AstQuery | AstValues | dict[str, Any]
"""
A node in a tree, representing a “query body” expression,
roughly: `SELECT ... [ {UNION|EXCEPT|INTERSECT} SELECT ...]`

See https://docs.rs/sqlparser/0.51.0/sqlparser/ast/enum.SetExpr.html
"""

Expr: TypeAlias = AstIdentifier | dict[str, Any]
"""
A SQL expression of any type.

See https://docs.rs/sqlparser/0.51.0/sqlparser/ast/enum.Expr.html
"""

Value: TypeAlias = dict[str, Any]
"""
Primitive SQL values such as number and string.

See https://docs.rs/sqlparser/0.51.0/sqlparser/ast/enum.Value.html
"""

TableFactor: TypeAlias = dict[str, Any]
"""
A table name or a parenthesized subquery with an optional alias.

See https://docs.rs/sqlparser/0.51.0/sqlparser/ast/enum.TableFactor.html
"""

JoinOperator: TypeAlias = dict[str, Any]
"""See https://docs.rs/sqlparser/0.51.0/sqlparser/ast/enum.JoinOperator.html"""

class One(TypedDict, Generic[T]):
    One: T

class Many(TypedDict, Generic[T]):
    Many: list[T]

class AstSelect(TypedDict):
    Select: Select

class AstSetVariable(TypedDict):
    SetVariable: SetVariable

class AstInsert(TypedDict):
    Insert: Insert

class AstIdentifier(TypedDict):
    """An identifier (e.g. table name or column name)"""

    Identifier: Ident

class AstCompoundIdentifier(TypedDict):
    """A multi-part identifier (e.g. table_alias.column or schema.table.col)"""

    CompoundIdentifier: list[Ident]

class AstValue(TypedDict):
    """A literal value, such as string, number, date or NULL."""

    Value: Value

class AstValues(TypedDict):
    """An insert VALUES clause."""

    Values: Values

class AstQuery(TypedDict):
    """
    A parenthesized subquery (SELECT ...),
    used in an expression like SELECT (subquery) AS x or WHERE (subquery) = x
    """

    Query: Query

class AstSubquery(TypedDict):
    """
    A parenthesized SELECT subquery.

    When part of a `SetExpr`, a subquery may include more set operations
    in its body and an optional ORDER BY / LIMIT.
    """

    Query: Query

class AstTable(TypedDict):
    Table: Table

class Ident(TypedDict):
    """An identifier, decomposed into its value or character data and the quote style."""

    value: str
    quote_style: Any | None

class SetVariable(TypedDict):
    """
    SET <variable> = expression;
    SET (variable[, ...]) = (expression[, ...]);
    """

    local: bool
    hivevar: bool
    variables: One[ObjectName] | Many[ObjectName]
    value: list[Expr]

class Select(TypedDict("Select", {"from": list[TableWithJoins]})):
    select_token: Any  # AttachedToken
    distinct: Any | None  # Option<Distinct>
    top: Any | None  # Option<Top,
    top_before_distinct: bool
    projection: list[Any]  # Vec<SelectItem>
    into: Any | None  # Option<SelectInto>
    lateral_views: list[Any]  # Vec<LateralView>
    prewhere: Expr | None
    selection: Expr | None
    group_by: Any  # GroupByExpr,
    cluster_by: list[Expr]
    distribute_by: list[Expr]
    sort_by: list[Expr]
    having: Expr | None
    named_window: list[Any]  # Vec<NamedWindowDefinition>
    qualify: Expr | None
    window_before_qualify: bool
    value_table_mode: Any | None  # Option<ValueTableMode>
    connect_by: Any | None  # Option<ConnectBy>

class Insert(TypedDict("Insert", {"or": Any | None})):
    """
    An INSERT statement.
    
    See https://docs.rs/sqlparser/0.51.0/sqlparser/ast/struct.Insert.html
    """

    ignore: bool
    into: bool
    table_name: ObjectName
    table_alias: Any | None
    columns: list[Ident]
    overwrite: bool
    source: Query | None
    """A SQL query that specifies what to insert"""
    partitioned: Any | None
    after_columns: list[Any]
    table: bool
    on: dict[str, Any] | None  # e.g. {"OnConflict": {"conflict_target": None, "action": "DoNothing"}},
    returning: Any | None
    replace_into: bool
    priority: Any | None
    insert_alias: Any | None

class Query(TypedDict("Query", {"with": Any | None})):
    """
    The most complete variant of a SELECT query expression,
    optionally including WITH, UNION / other set operations, and ORDER BY.
    """

    body: SetExpr
    order_by: Any | None
    limit: Any | None
    limit_by: list[Any]
    offset: Any | None
    fetch: Any | None
    locks: list[Any]
    for_clause: Any | None
    settings: Any | None
    format_clause: Any | None

class Values(TypedDict):
    explicit_row: bool
    rows: list[list[Expr]]

class TableWithJoins(TypedDict):
    relation: TableFactor
    joins: list[Join]

class Join(TypedDict("Join", {"global": bool})):
    relation: TableFactor
    join_operator: JoinOperator

class Table(TypedDict):
    name: ObjectName
    alias: Any | None  # Option<TableAlias>
    args: Any | None  # Option<TableFunctionArgs>
    with_hints: list[Expr]
    version: Any | None  # Option<TableVersion>
    with_ordinality: bool
    partitions: list[Ident]
    json_path: Any | None  # Option<JsonPath>
    sample: Any | None  # Option<TableSampleKind>
