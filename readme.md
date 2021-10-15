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
------------------------------------------------------------------------------------------- benchmark: 4 tests -------------------------------------------------------------------------------------------
Name (time in us)            Min                    Max                  Mean              StdDev                Median                 IQR            Outliers          OPS            Rounds  Iterations
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_sqloxide            27.1800 (1.0)          65.9700 (1.0)         28.0709 (1.0)        2.5352 (1.0)         27.6100 (1.0)        0.2400 (1.0)        49;179  35,624.0263 (1.0)        1611           1
test_sqlglot            744.6920 (27.40)     1,067.4020 (16.18)      776.8493 (27.67)     33.7054 (13.30)      761.0070 (27.56)     37.4755 (156.14)     166;44   1,287.2510 (0.04)       1000           1
test_sqlparser        1,504.1130 (55.34)     8,023.3680 (121.62)   1,574.6767 (56.10)    276.0027 (108.87)   1,549.5140 (56.12)     48.2877 (201.18)       1;15     635.0510 (0.02)        561           1
test_mozsqlparser     2,574.9760 (94.74)    13,915.5610 (210.94)   2,874.2035 (102.39)   984.6498 (388.40)   2,733.3170 (99.00)    237.4610 (989.34)        4;4     347.9225 (0.01)        324           1
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

## Example

The `depgraph` example reads a bunch of `.sql` files from disk using glob, and builds a dependency graph of all of the objects using graphviz.

```
poetry run python ./examples/depgraph.py --path {path/to/folder/with/queries} 
```

## Develop

1) Install `rustup`

2) `poetry install` will automatically create the venv, compile the package and install it into the venv via the build script.
