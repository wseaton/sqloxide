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
-------------------------------------------------------------------------------------------- benchmark: 4 tests --------------------------------------------------------------------------------------------
Name (time in us)            Min                    Max                  Mean                StdDev                Median                 IQR            Outliers          OPS            Rounds  Iterations
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_sqloxide            24.0300 (1.0)          38.8500 (1.0)         24.6345 (1.0)          0.7415 (1.0)         24.4900 (1.0)        0.1803 (1.0)       440;666  40,593.5484 (1.0)        9149           1
test_sqlglot            847.1730 (35.25)     1,315.9550 (33.87)      868.1668 (35.24)       27.2481 (36.75)      859.0330 (35.08)      8.2075 (45.53)     147;150   1,151.8524 (0.03)       1009           1
test_sqlparser        1,459.7250 (60.75)     8,096.5180 (208.40)   1,522.3935 (61.80)      280.2361 (377.95)   1,496.5750 (61.11)     43.1950 (239.64)       6;27     656.8604 (0.02)        581           1
test_mozsqlparser     2,596.4290 (108.05)   12,285.0920 (316.22)   2,912.9214 (118.25)   1,025.7038 (>1000.0)  2,762.9745 (112.82)   238.0710 (>1000.0)       4;6     343.2980 (0.01)        316           1
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

## Example

The `depgraph` example reads a bunch of `.sql` files from disk using glob, and builds a dependency graph of all of the objects using graphviz.

```
poetry run python ./examples/depgraph.py --path {path/to/folder/with/queries} 
```

## Develop

1) Install `rustup`

2) `poetry install` will automatically create the venv, compile the package and install it into the venv via the build script.
