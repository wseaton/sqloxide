use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

use pythonize::pythonize;

use sqlparser::dialect::*;
use sqlparser::parser::Parser;

fn string_to_dialect(dialect: &str) -> Box<dyn Dialect> {
    match dialect.to_lowercase().as_str() {
        "ansi" => Box::new(AnsiDialect {}),
        "bigquery" | "bq" => Box::new(BigQueryDialect {}),
        "clickhouse" => Box::new(ClickHouseDialect {}),
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
        Ok(statements) => {
            pythonize(py, &statements).expect("Internal python serialization failed.")
        }
        Err(_e) => {
            let msg = _e.to_string();
            return Err(PyValueError::new_err(format!(
                "Query parsing failed.\n\t{}",
                msg
            )));
        }
    };

    Ok(output)
}

#[pymodule]
fn sqloxide(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_sql, m)?)?;
    Ok(())
}
