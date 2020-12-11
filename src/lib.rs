use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::exceptions::PyValueError;
use pyo3::Python;

use sqlparser::dialect::*;
use sqlparser::parser::Parser;


#[pyfunction]
fn parse_sql(_py: Python, sql: &str) -> PyResult<String> {
    let dialect = GenericDialect {};
    let parse_result =
        Parser::parse_sql(&dialect, sql);

    let json_output = match parse_result {
        Ok(statements) => serde_json::to_string(&statements).unwrap_or("[]".to_string()),
        Err(_e) => return Err(PyValueError::new_err("Parsing failed."))
    };

    Ok(json_output)
}

#[pymodule]
fn sqloxide(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_sql, m)?)?;
    Ok(())
}
