from typing import Any, Callable, Generic, Literal, TypeAlias, TypedDict, TypeVar

Dialect: TypeAlias = Literal[
    "generic",
    "ansi",
    "bigquery",
    "clickhouse",
    "databricks",
    "duckdb",
    "hive",
    "mssql",
    "mysql",
    "postgresql",
    "postgres",
    "redshift",
    "snowflake",
    "sqlite",
    "oracle",
]

def parse_sql(sql: str, dialect: Dialect) -> list[Statement]: ...
def restore_ast(ast: list[Statement]) -> list[str]: ...
def extract_relations(parsed_query: list[Statement]) -> list[ObjectName]: ...
def mutate_relations(parsed_query: list[Statement], func: Callable[[str], str]) -> list[str]: ...
def extract_expressions(parsed_query: list[Statement]) -> list[Expr]: ...
def mutate_expressions(parsed_query: list[Statement], func: Callable[[Expr], Expr]) -> list[str]: ...

T = TypeVar("T")

# ---------------------------------------------------------------------------
# Core identifier types
# ---------------------------------------------------------------------------

class Span(TypedDict):
    start: SourceLocation
    end: SourceLocation

class SourceLocation(TypedDict):
    line: int
    column: int

class Ident(TypedDict):
    """An identifier, decomposed into its value or character data and the quote style."""
    value: str
    quote_style: str | None
    span: Span

class ObjectNamePartIdentifier(TypedDict):
    Identifier: Ident

class ObjectNamePartFunction(TypedDict):
    Function: dict[str, Any]

ObjectNamePart: TypeAlias = ObjectNamePartIdentifier | ObjectNamePartFunction
"""
A component of an ObjectName. Usually an Identifier, but can be a
Function for Snowflake's IDENTIFIER(...) syntax.
"""

ObjectName: TypeAlias = list[ObjectNamePart]
"""
A name of a table, view, custom type, etc.
(possibly multi-part, i.e. db.schema.obj)
"""

# ---------------------------------------------------------------------------
# Statement types
#
# See https://docs.rs/sqlparser/0.61.0/sqlparser/ast/enum.Statement.html
# ---------------------------------------------------------------------------

Statement: TypeAlias = AstQuery | AstInsert | AstUpdate | AstDelete | AstCreateTable | AstCreateView | dict[str, Any]
"""
A top-level statement (SELECT, INSERT, CREATE, etc.)

Common variants are typed below. Less common variants appear as
dict[str, Any] with the variant name as key.
"""

# ---------------------------------------------------------------------------
# SetExpr / Query body
# ---------------------------------------------------------------------------

SetExpr: TypeAlias = AstSelect | AstSetOperation | AstValues | AstQuery | dict[str, Any]
"""
A node in a tree, representing a "query body" expression,
roughly: `SELECT ... [ {UNION|EXCEPT|INTERSECT} SELECT ...]`

See https://docs.rs/sqlparser/0.61.0/sqlparser/ast/enum.SetExpr.html
"""

# ---------------------------------------------------------------------------
# Expr
# ---------------------------------------------------------------------------

Expr: TypeAlias = AstIdentifier | AstCompoundIdentifier | AstBinaryOp | AstUnaryOp | AstValue | AstFunction | AstNested | dict[str, Any]
"""
A SQL expression of any type.

See https://docs.rs/sqlparser/0.61.0/sqlparser/ast/enum.Expr.html
"""

Value: TypeAlias = dict[str, Any]
"""
Primitive SQL values such as number and string.

See https://docs.rs/sqlparser/0.61.0/sqlparser/ast/enum.Value.html
"""

TableFactor: TypeAlias = dict[str, Any]
"""
A table name or a parenthesized subquery with an optional alias.

See https://docs.rs/sqlparser/0.61.0/sqlparser/ast/enum.TableFactor.html
"""

JoinOperator: TypeAlias = dict[str, Any]
"""See https://docs.rs/sqlparser/0.61.0/sqlparser/ast/enum.JoinOperator.html"""

# ---------------------------------------------------------------------------
# Wrapper TypedDicts for enum variant serialization
# ---------------------------------------------------------------------------

class One(TypedDict, Generic[T]):
    One: T

class Many(TypedDict, Generic[T]):
    Many: list[T]

class AstQuery(TypedDict):
    Query: Query

class AstSelect(TypedDict):
    Select: Select

class AstSetOperation(TypedDict):
    SetOperation: dict[str, Any]

class AstInsert(TypedDict):
    Insert: Insert

class AstUpdate(TypedDict):
    Update: Update

class AstDelete(TypedDict):
    Delete: Delete

class AstCreateTable(TypedDict):
    CreateTable: dict[str, Any]

class AstCreateView(TypedDict):
    CreateView: dict[str, Any]

class AstIdentifier(TypedDict):
    """An identifier (e.g. table name or column name)"""
    Identifier: Ident

class AstCompoundIdentifier(TypedDict):
    """A multi-part identifier (e.g. table_alias.column or schema.table.col)"""
    CompoundIdentifier: list[Ident]

class AstBinaryOp(TypedDict):
    BinaryOp: BinaryOp

class AstUnaryOp(TypedDict):
    UnaryOp: UnaryOp

class AstValue(TypedDict):
    """A literal value, such as string, number, date or NULL."""
    Value: Value

class AstValues(TypedDict):
    """An insert VALUES clause."""
    Values: Values

class AstFunction(TypedDict):
    Function: dict[str, Any]

class AstNested(TypedDict):
    Nested: Expr

class AstSubquery(TypedDict):
    """A parenthesized SELECT subquery."""
    Query: Query

class AstTable(TypedDict):
    Table: Table

# ---------------------------------------------------------------------------
# Struct definitions
# ---------------------------------------------------------------------------

class BinaryOp(TypedDict):
    left: Expr
    op: str
    right: Expr

class UnaryOp(TypedDict):
    op: str
    expr: Expr

class Query(TypedDict("Query", {"with": Any | None})):
    """
    The most complete variant of a SELECT query expression,
    optionally including WITH, UNION / other set operations, and ORDER BY.

    See https://docs.rs/sqlparser/0.61.0/sqlparser/ast/struct.Query.html
    """
    body: SetExpr
    order_by: Any | None
    limit_clause: Any | None
    fetch: Any | None
    locks: list[Any]
    for_clause: Any | None
    settings: Any | None
    format_clause: Any | None
    pipe_operators: list[Any]

class Select(TypedDict("Select", {"from": list["TableWithJoins"]})):
    """See https://docs.rs/sqlparser/0.61.0/sqlparser/ast/struct.Select.html"""
    select_token: Any  # AttachedToken
    optimizer_hint: Any | None
    distinct: Any | None
    select_modifiers: Any | None
    top: Any | None
    top_before_distinct: bool
    projection: list[Any]  # Vec<SelectItem>
    exclude: Any | None
    into: Any | None  # Option<SelectInto>
    lateral_views: list[Any]
    prewhere: Expr | None
    selection: Expr | None
    connect_by: list[Any]
    group_by: Any  # GroupByExpr
    cluster_by: list[Expr]
    distribute_by: list[Expr]
    sort_by: list[Any]  # Vec<OrderByExpr>
    having: Expr | None
    named_window: list[Any]
    qualify: Expr | None
    window_before_qualify: bool
    value_table_mode: Any | None
    flavor: Any  # SelectFlavor

class Insert(TypedDict("Insert", {"or": Any | None})):
    """
    An INSERT statement.

    See https://docs.rs/sqlparser/0.61.0/sqlparser/ast/struct.Insert.html
    """
    insert_token: Any  # AttachedToken
    optimizer_hint: Any | None
    ignore: bool
    into: bool
    table: Any  # TableObject
    table_alias: Ident | None
    columns: list[Ident]
    overwrite: bool
    source: Query | None
    assignments: list[Any]
    partitioned: Any | None
    after_columns: list[Ident]
    has_table_keyword: bool
    on: dict[str, Any] | None
    returning: Any | None
    replace_into: bool
    priority: Any | None
    insert_alias: Any | None
    settings: Any | None
    format_clause: Any | None

class Update(TypedDict):
    """
    An UPDATE statement.

    See https://docs.rs/sqlparser/0.61.0/sqlparser/ast/struct.Update.html
    """
    table: "TableWithJoins"
    assignments: list[Any]
    from_: Any | None
    selection: Expr | None
    returning: Any | None
    or: Any | None

class Delete(TypedDict):
    """
    A DELETE statement.

    See https://docs.rs/sqlparser/0.61.0/sqlparser/ast/struct.Delete.html
    """
    tables: list[ObjectName]
    from_: Any  # FromTable
    using: Any | None
    selection: Expr | None
    returning: Any | None
    order_by: list[Any]
    limit: Expr | None

class Values(TypedDict):
    explicit_row: bool
    rows: list[list[Expr]]

class TableWithJoins(TypedDict):
    relation: TableFactor
    joins: list["Join"]

class Join(TypedDict("Join", {"global": bool})):
    relation: TableFactor
    join_operator: JoinOperator

class TableAlias(TypedDict):
    explicit: bool
    name: Ident
    columns: list["TableAliasColumnDef"]

class TableAliasColumnDef(TypedDict):
    name: Ident
    data_type: Any | None

class Table(TypedDict):
    name: ObjectName
    alias: TableAlias | None
    args: Any | None
    with_hints: list[Expr]
    version: Any | None
    with_ordinality: bool
    partitions: list[Ident]
    json_path: Any | None
    sample: Any | None
