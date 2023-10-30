use pythonize::pythonize;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use pyo3::wrap_pyfunction;
use pythonize::PythonizeError;

use sqlparser::ast::Statement;
use sqlparser::dialect::*;
use sqlparser::parser::Parser;

mod visitor;
use visitor::{extract_expressions, extract_relations, mutate_expressions, mutate_relations};

fn string_to_dialect(dialect: &str) -> Box<dyn Dialect> {
    match dialect.to_lowercase().as_str() {
        "ansi" => Box::new(AnsiDialect {}),
        "bigquery" | "bq" => Box::new(BigQueryDialect {}),
        "clickhouse" => Box::new(ClickHouseDialect {}),
        "duckdb" => Box::new(DuckDbDialect {}),
        "generic" => Box::new(GenericDialect {}),
        "hive" => Box::new(HiveDialect {}),
        "ms" | "mssql" => Box::new(MsSqlDialect {}),
        "mysql" => Box::new(MySqlDialect {}),
        "postgres" => Box::new(PostgreSqlDialect {}),
        "redshift" => Box::new(RedshiftSqlDialect {}),
        "snowflake" => Box::new(SnowflakeDialect {}),
        "sqlite" => Box::new(SQLiteDialect {}),
        _ => {
            println!("The dialect you chose was not recognized, falling back to 'generic'");
            Box::new(GenericDialect {})
        }
    }
}

/// Function to parse SQL statements from a string. Returns a list with
/// one item per query statement.
///
/// Available `dialects`:
/// - generic
/// - ansi
/// - duckdb
/// - hive
/// - ms (mssql)
/// - mysql
/// - postgres
/// - snowflake
/// - sqlite
/// - clickhouse
/// - redshift
/// - bigquery (bq)
///
#[pyfunction]
#[pyo3(text_signature = "(sql, dialect)")]
fn parse_sql(py: Python, sql: &str, dialect: &str) -> PyResult<PyObject> {
    let chosen_dialect = string_to_dialect(dialect);
    let parse_result = Parser::parse_sql(&*chosen_dialect, sql);

    let output = match parse_result {
        Ok(statements) => pythonize(py, &statements).map_err(|e| {
            let msg = e.to_string();
            PyValueError::new_err(format!("Python object serialization failed.\n\t{msg}"))
        })?,
        Err(e) => {
            let msg = e.to_string();
            return Err(PyValueError::new_err(format!(
                "Query parsing failed.\n\t{msg}"
            )));
        }
    };

    Ok(output)
}

/// This utility function allows reconstituing a modified AST back into list of SQL queries.
#[pyfunction]
#[pyo3(text_signature = "(ast)")]
fn restore_ast(_py: Python, ast: &PyAny) -> PyResult<Vec<String>> {
    let parse_result: Result<Vec<Statement>, PythonizeError> = pythonize::depythonize(ast);

    let output = match parse_result {
        Ok(statements) => statements,
        Err(e) => {
            let msg = e.to_string();
            return Err(PyValueError::new_err(format!(
                "Query serialization failed.\n\t{msg}"
            )));
        }
    };

    Ok(output
        .iter()
        .map(std::string::ToString::to_string)
        .collect::<Vec<String>>())
}

#[pymodule]
fn sqloxide(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_sql, m)?)?;
    m.add_function(wrap_pyfunction!(restore_ast, m)?)?;
    // TODO: maybe refactor into seperate module
    m.add_function(wrap_pyfunction!(extract_relations, m)?)?;
    m.add_function(wrap_pyfunction!(mutate_relations, m)?)?;
    m.add_function(wrap_pyfunction!(extract_expressions, m)?)?;
    m.add_function(wrap_pyfunction!(mutate_expressions, m)?)?;
    Ok(())
}
