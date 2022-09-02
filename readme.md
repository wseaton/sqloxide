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
test_sqloxide            29.6800 (1.0)          50.4300 (1.0)         30.6219 (1.0)        0.7367 (1.0)         30.4900 (1.0)        0.2390 (1.0)       527;716  32,656.3811 (1.0)        9099           1
test_sqlglot            365.8420 (12.33)       692.8950 (13.74)      377.2422 (12.32)     11.7692 (15.98)      375.7825 (12.32)      4.3145 (18.05)       62;97   2,650.8168 (0.08)       2260           1
test_sqlparser        1,577.7720 (53.16)     9,751.9699 (193.38)   1,651.5547 (53.93)    355.5511 (482.64)   1,620.7315 (53.16)     30.9200 (129.37)       3;60     605.4901 (0.02)        538           1
test_mozsqlparser     2,793.8400 (94.13)    12,358.7790 (245.07)   3,091.8519 (100.97)   960.4173 (>1000.0)  2,937.6310 (96.35)    243.3220 (>1000.0)       4;4     323.4308 (0.01)        316           1
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
