use pyo3::prelude::*;
use pyo3::wrap_pyfunction;
use pyo3::exceptions::PyValueError;
use pyo3::Python;

use pythonize::pythonize;

use sqlparser::dialect::*;
use sqlparser::parser::Parser;

fn string_to_dialect(dialect: &str) -> Box<dyn Dialect> {
    match dialect {
        "generic" => Box::new(GenericDialect {}),
        "ansi" => Box::new(AnsiDialect {}),
        "ms" => Box::new(MsSqlDialect {}),
        "postgres" => Box::new(PostgreSqlDialect {}),
        _ => Box::new(GenericDialect {})
    }
}


/// Function to parse SQL statements from a string. Returns a list with
/// one item per query statement.
#[pyfunction]
#[text_signature = "(sql, dialect)"]
fn parse_sql(_py: Python, sql: &str, dialect: &str)  -> PyResult<PyObject> {
    
    let gil = Python::acquire_gil();
    let py = gil.python();
    
    let chosen_dialect = string_to_dialect(dialect);
    let parse_result =
        Parser::parse_sql(&*chosen_dialect, sql);

    let output = match parse_result {
        Ok(statements) => pythonize(py, &statements).unwrap(),
        Err(_e) => return Err(PyValueError::new_err("Parsing failed."))
    };

    Ok(output)
}

#[pymodule]
fn sqloxide(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_sql, m)?)?;
    Ok(())
}
