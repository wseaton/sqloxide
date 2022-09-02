# sqloxide

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/wseaton/sqloxide/CI)

`sqloxide` wraps rust bindings for [sqlparser-rs](https://github.com/ballista-compute/sqlparser-rs) into a python package using `pyO3`.

The original goal of this project was to have a very fast, efficient, and accurate SQL parser I could use for building data lineage graphs across large code bases (think hundreds of auto-generated .sql files). Most existing sql parsing approaches for python are either very slow or not accurate (especially in regards to deeply nested queries, sub-selects and/or table aliases). Looking to the rust community for support, I found the excellent `sqlparser-rs` crate which is quite easy to wrap in python code.

## Installation

The project provides `manylinux2014` wheels on pypi so it should be compatible with most linux distributions. Native wheels are also now available for OSX and Windows.

To install from pypi:
```sh
pip install sqloxide
```

## Usage

```python 
from sqloxide import parse_sql

sql = """
SELECT employee.first_name, employee.last_name,
       call.start_time, call.end_time, call_outcome.outcome_text
FROM employee
INNER JOIN call ON call.employee_id = employee.id
INNER JOIN call_outcome ON call.call_outcome_id = call_outcome.id
ORDER BY call.start_time ASC;
"""

output = parse_sql(sql=sql, dialect='ansi')

print(output)

>>> [
  {
    "Query": {
      "ctes": [],
      "body": {
        "Select": {
          "distinct": false,
          "top": null,
          "projection": [
            {
              "UnnamedExpr": {
                "CompoundIdentifier": [
                  {
                    "value": "employee",
                    "quote_style": null
                  },
                  {
                    "value": "first_name",
                    "quote_style": null
                  }
                ]
              }
            },
            {
              "UnnamedExpr": {
                "CompoundIdentifier": [
                  {
                    "value": "employee",
                    "quote_style": null
                  },
                  {
                    "value": "last_name",
                    "quote_style": null
                  }
                ]
              }
            },
            {
              "UnnamedExpr": {
                "CompoundIdentifier": [
                  {
                    "value": "call",
                    "quote_style": null
                  },
                  {
                    "value": "start_time",
                    "quote_style": null
                  }
                ]
              }
            },
            { # OUTPUT TRUNCATED
```
## Benchmarks

We run 4 benchmarks, comparing to some python native sql parsing libraries:

* `test_sqloxide` - parse query and get a python object back from rust 
* `test_sqlparser` - testing [sqlparse](https://pypi.org/project/sqlparse/), query -> AST
* `test_mozsqlparser` - testing [moz-sql-parser](https://pypi.org/project/moz-sql-parser/), full roundtrip as in the docs, query -> JSON
* `test_sqlglot` - testing [sqlglot](https://github.com/tobymao/sqlglot/), query -> AST


To run them on your machine:

```
poetry run pytest tests/benchmark.py
```

```
------------------------------------------------------------------------------------------- benchmark: 4 tests ------------------------------------------------------------------------------------------
Name (time in us)            Min                   Max                  Mean              StdDev                Median                 IQR            Outliers          OPS            Rounds  Iterations
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_sqloxide            26.6800 (1.0)         58.4100 (1.0)         27.5952 (1.0)        2.3653 (1.0)         27.2300 (1.0)        0.3001 (1.0)       121;310  36,238.2428 (1.0)        4622           1
test_sqlglot            646.0550 (24.21)      932.9370 (15.97)      668.1087 (24.21)     26.1988 (11.08)      659.3050 (24.21)      8.2647 (27.54)     171;184   1,496.7624 (0.04)       1355           1
test_sqlparser        1,551.8610 (58.17)    2,255.7170 (38.62)    1,625.3044 (58.90)     74.4809 (31.49)    1,605.4370 (58.96)     38.4900 (128.27)      29;33     615.2694 (0.02)        542           1
test_mozsqlparser     2,798.2310 (104.88)   9,845.7520 (168.56)   3,051.8365 (110.59)   745.5932 (315.22)   2,932.6010 (107.70)   237.6895 (792.14)        4;4     327.6715 (0.01)        293           1
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

## Example

The `depgraph` example reads a bunch of `.sql` files from disk using glob, and builds a dependency graph of all of the objects using graphviz.

```
poetry run python ./examples/depgraph.py --path {path/to/folder/with/queries} 
```

## Develop

1) Install `rustup`

2) `poetry install` will automatically create the venv, compile the package and install it into the venv via the build script.
