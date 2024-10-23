use core::ops::ControlFlow;

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use serde::Serialize;

use sqlparser::ast::{
    Statement, {visit_expressions, visit_expressions_mut, visit_relations, visit_relations_mut},
};

// Refactored function for handling depythonization
fn depythonize_query(parsed_query: &Bound<'_, PyAny>) -> Result<Vec<Statement>, PyErr> {
    match pythonize::depythonize(parsed_query) {
        Ok(statements) => Ok(statements),
        Err(e) => {
            let msg = e.to_string();
            Err(PyValueError::new_err(format!(
                "Query serialization failed.\n\t{msg}"
            )))
        }
    }
}

fn pythonize_query_output<T>(py: Python, output: Vec<T>) -> PyResult<Py<PyAny>>
where
    T: Sized + Serialize,
{
    match pythonize::pythonize(py, &output) {
        Ok(p) => Ok(p.into()),
        Err(e) => {
            let msg = e.to_string();
            Err(PyValueError::new_err(format!(
                "Python object serialization failed.\n\t{msg}"
            )))
        }
    }
}

#[pyfunction]
#[pyo3(text_signature = "(parsed_query)")]
pub fn extract_relations(py: Python, parsed_query: &Bound<'_, PyAny>) -> PyResult<PyObject> {
    let statements = depythonize_query(parsed_query)?;

    let mut relations = Vec::new();
    for statement in statements {
        visit_relations(&statement, |relation| {
            relations.push(relation.clone());
            ControlFlow::<()>::Continue(())
        });
    }

    pythonize_query_output(py, relations)
}

#[pyfunction]
#[pyo3(text_signature = "(parsed_query, func)")]
pub fn mutate_relations(_py: Python, parsed_query: &Bound<'_, PyAny>, func: &Bound<'_, PyAny>) -> PyResult<Vec<String>> {
    let mut statements = depythonize_query(parsed_query)?;

    for statement in &mut statements {
        visit_relations_mut(statement, |table| {
            for section in &mut table.0 {
                let val = match func.call1((section.value.clone(),)) {
                    Ok(val) => val,
                    Err(e) => {
                        let msg = e.to_string();
                        return ControlFlow::Break(PyValueError::new_err(format!(
                            "Python object serialization failed.\n\t{msg}"
                        )));
                    }
                };

                section.value = val.to_string();
            }
            ControlFlow::Continue(())
        });
    }

    Ok(statements
        .iter()
        .map(std::string::ToString::to_string)
        .collect::<Vec<String>>())
}

#[pyfunction]
#[pyo3(text_signature = "(parsed_query, func)")]
pub fn mutate_expressions(py: Python, parsed_query: &Bound<'_, PyAny>, func: &Bound<'_, PyAny>) -> PyResult<Vec<String>> {
    let mut statements: Vec<Statement> = depythonize_query(parsed_query)?;

    for statement in &mut statements {
        visit_expressions_mut(statement, |expr| {
            let converted_expr = match pythonize::pythonize(py, expr) {
                Ok(val) => val,
                Err(e) => {
                    let msg = e.to_string();
                    return ControlFlow::Break(PyValueError::new_err(format!(
                        "Python object deserialization failed.\n\t{msg}"
                    )));
                }
            };

            let func_result = match func.call1((converted_expr,)) {
                Ok(val) => val,
                Err(e) => {
                    let msg = e.to_string();
                    return ControlFlow::Break(PyValueError::new_err(format!(
                        "Calling python function failed.\n\t{msg}"
                    )));
                }
            };

            *expr = match pythonize::depythonize(&func_result) {
                Ok(val) => val,
                Err(e) => {
                    let msg = e.to_string();
                    return ControlFlow::Break(PyValueError::new_err(format!(
                        "Python object reserialization failed.\n\t{msg}"
                    )));
                }
            };

            ControlFlow::Continue(())
        });
    }

    Ok(statements
        .iter()
        .map(std::string::ToString::to_string)
        .collect::<Vec<String>>())
}

#[pyfunction]
#[pyo3(text_signature = "(parsed_query)")]
pub fn extract_expressions(py: Python, parsed_query: &Bound<'_, PyAny>) -> PyResult<PyObject> {
    let statements: Vec<Statement> = depythonize_query(parsed_query)?;

    let mut expressions = Vec::new();
    for statement in statements {
        visit_expressions(&statement, |expr| {
            expressions.push(expr.clone());
            ControlFlow::<()>::Continue(())
        });
    }

    pythonize_query_output(py, expressions)
}
