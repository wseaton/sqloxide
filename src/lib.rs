use pythonize::pythonize;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use pythonize::PythonizeError;

use sqlparser::ast::Statement;
use sqlparser::dialect::dialect_from_str;
use sqlparser::dialect::*;
use sqlparser::parser::Parser;

mod visitor;
use visitor::{extract_expressions, extract_relations, mutate_expressions, mutate_relations};

/// Function to parse SQL statements from a string. Returns a list with
/// one item per query statement.
///
/// Available `dialects`: https://github.com/sqlparser-rs/sqlparser-rs/blob/main/src/dialect/mod.rs#L189-L206
#[pyfunction]
#[pyo3(text_signature = "(sql, dialect)")]
fn parse_sql(py: Python, sql: String, dialect: String) -> PyResult<PyObject> {
    let chosen_dialect = dialect_from_str(dialect).unwrap_or_else(|| {
        println!("The dialect you chose was not recognized, falling back to 'generic'");
        Box::new(GenericDialect {})
    });
    let parse_result = Parser::parse_sql(&*chosen_dialect, &sql);

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

    Ok(output.into())
}

/// This utility function allows reconstituing a modified AST back into list of SQL queries.
#[pyfunction]
#[pyo3(text_signature = "(ast)")]
fn restore_ast(_py: Python, ast: &Bound<'_, PyAny>) -> PyResult<Vec<String>> {
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
fn sqloxide(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_sql, m)?)?;
    m.add_function(wrap_pyfunction!(restore_ast, m)?)?;
    // TODO: maybe refactor into seperate module
    m.add_function(wrap_pyfunction!(extract_relations, m)?)?;
    m.add_function(wrap_pyfunction!(mutate_relations, m)?)?;
    m.add_function(wrap_pyfunction!(extract_expressions, m)?)?;
    m.add_function(wrap_pyfunction!(mutate_expressions, m)?)?;
    Ok(())
}
