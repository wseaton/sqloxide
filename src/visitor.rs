use core::ops::ControlFlow;
use pythonize::pythonize;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use pythonize::PythonizeError;

use sqlparser::ast::{
    Statement, {visit_expressions, visit_expressions_mut, visit_relations, visit_relations_mut},
};

///
/// Function to extract relations from a parsed query.
/// Returns a nested list of relations, one list per query statement.
///
/// Example:
/// ```python
/// from sqloxide import parse_sql, extract_relations
///
/// sql = "SELECT * FROM table1 JOIN table2 ON table1.id = table2.id"
/// parsed_query = parse_sql(sql, "generic")
/// relations = extract_relations(parsed_query)
/// print(relations)
/// ```
///
#[pyfunction]
#[pyo3(text_signature = "(parsed_query)")]
pub fn extract_relations(py: Python, parsed_query: &PyAny) -> PyResult<PyObject> {
    let parse_result: Result<Vec<Statement>, PythonizeError> = pythonize::depythonize(parsed_query);

    let mut relations = Vec::new();

    match parse_result {
        Ok(statements) => {
            for statement in statements {
                visit_relations(&statement, |relation| {
                    relations.push(relation.clone());
                    ControlFlow::<()>::Continue(())
                });
            }
        }
        Err(e) => {
            let msg = e.to_string();
            return Err(PyValueError::new_err(format!(
                "Query serialization failed.\n\t{msg}"
            )));
        }
    };

    let output = pythonize(py, &relations).expect("Internal python deserialization failed.");

    Ok(output)
}

/// This function takes a parsed query object and a callable 1 argument `function`,
/// and applies the function to each relation in the query.
///
/// It returns a string with the mutated query.
#[pyfunction]
#[pyo3(text_signature = "(parsed_query, func)")]
pub fn mutate_relations(_py: Python, parsed_query: &PyAny, func: &PyAny) -> PyResult<Vec<String>> {
    let parse_result: Result<Vec<Statement>, PythonizeError> = pythonize::depythonize(parsed_query);

    let output = match parse_result {
        Ok(mut statements) => {
            for statement in &mut statements {
                visit_relations_mut(statement, |table| {
                    for section in &mut table.0 {
                        section.value = func
                            .call1((section.value.clone(),))
                            .expect("failed to call function")
                            .to_string();
                    }
                    ControlFlow::<()>::Continue(())
                });
            }
            statements
        }
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

#[pyfunction]
#[pyo3(text_signature = "(parsed_query, func)")]
pub fn mutate_expressions(
    _py: Python,
    parsed_query: &PyAny,
    func: &PyAny,
) -> PyResult<Vec<String>> {
    let parse_result: Result<Vec<Statement>, PythonizeError> = pythonize::depythonize(parsed_query);

    let output = match parse_result {
        Ok(mut statements) => {
            for statement in &mut statements {
                visit_expressions_mut(statement, |expr| {
                    let converted_expr =
                        pythonize::pythonize(_py, expr).expect("Failed to serialize");

                    *expr = pythonize::depythonize(
                        func.call1((converted_expr,))
                            .expect("failed to call function"),
                    )
                    .expect("failed to deserialize");
                    ControlFlow::<()>::Continue(())
                });
            }
            statements
        }
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

#[pyfunction]
#[pyo3(text_signature = "(parsed_query)")]
pub fn extract_expressions(py: Python, parsed_query: &PyAny) -> PyResult<PyObject> {
    let parse_result: Result<Vec<Statement>, PythonizeError> = pythonize::depythonize(parsed_query);

    let mut expressions = Vec::new();

    match parse_result {
        Ok(statements) => {
            for statement in statements {
                visit_expressions(&statement, |expr| {
                    expressions.push(expr.clone());
                    ControlFlow::<()>::Continue(())
                });
            }
        }
        Err(e) => {
            let msg = e.to_string();
            return Err(PyValueError::new_err(format!(
                "Query serialization failed.\n\t{msg}"
            )));
        }
    };

    let output = pythonize(py, &expressions).expect("Internal python deserialization failed.");

    Ok(output)
}
