use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use pyo3::wrap_pyfunction;
use pythonize::PythonizeError;
use sqlparser::ast::visit_relations_mut;
use sqlparser::ast::Statement;

use core::ops::ControlFlow;
use pythonize::pythonize;
use sqlparser::ast::visit_relations;
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
fn extract_relations(py: Python, parsed_query: &PyAny) -> PyResult<PyObject> {
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
        Err(_e) => {
            let msg = _e.to_string();
            return Err(PyValueError::new_err(format!(
                "Query serialization failed.\n\t{}",
                msg
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
fn mutate_relations(_py: Python, parsed_query: &PyAny, func: &PyAny) -> PyResult<Vec<String>> {
    let parse_result: Result<Vec<Statement>, PythonizeError> = pythonize::depythonize(parsed_query);

    let output = match parse_result {
        Ok(mut statements) => {
            for statement in &mut statements {
                visit_relations_mut(statement, |table| {
                    for section in table.0.iter_mut() {
                        section.value = func
                            .call1((section.value.to_owned(),))
                            .expect("failed to call function")
                            .to_string();
                    }
                    ControlFlow::<()>::Continue(())
                });
            }
            statements
        }
        Err(_e) => {
            let msg = _e.to_string();
            return Err(PyValueError::new_err(format!(
                "Query serialization failed.\n\t{}",
                msg
            )));
        }
    };

    Ok(output
        .iter()
        .map(|x| x.to_string())
        .collect::<Vec<String>>())
}

/// This utility function allows reconstituing a modified AST back into list of SQL queries.
#[pyfunction]
#[pyo3(text_signature = "(ast)")]
fn restore_ast(_py: Python, ast: &PyAny) -> PyResult<Vec<String>> {
    let parse_result: Result<Vec<Statement>, PythonizeError> = pythonize::depythonize(ast);

    let output = match parse_result {
        Ok(statements) => statements,
        Err(_e) => {
            let msg = _e.to_string();
            return Err(PyValueError::new_err(format!(
                "Query serialization failed.\n\t{}",
                msg
            )));
        }
    };

    Ok(output
        .iter()
        .map(|x| x.to_string())
        .collect::<Vec<String>>())
}

#[pymodule]
fn sqloxide(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_sql, m)?)?;
    m.add_function(wrap_pyfunction!(extract_relations, m)?)?;
    m.add_function(wrap_pyfunction!(mutate_relations, m)?)?;
    m.add_function(wrap_pyfunction!(restore_ast, m)?)?;
    Ok(())
}
