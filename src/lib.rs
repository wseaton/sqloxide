use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

use pyo3::Python;

use sqlparser::dialect::*;
use sqlparser::parser::Parser;


#[pyfunction]
fn parse_sql(_py: Python, sql: &str) -> PyResult<String> {
    let dialect = GenericDialect {};
    let parse_result =
        Parser::parse_sql(&dialect, sql).expect("sqlparser-rs failed to parse your query.");
    let res = serde_json::to_string_pretty(&parse_result).unwrap_or("[]".to_string());

    Ok(res)
}

#[pymodule]
fn sqloxide(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_sql, m)?)?;
    Ok(())
}
