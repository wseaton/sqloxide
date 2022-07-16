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
test_sqloxide            25.8210 (1.0)          45.6700 (1.0)         26.4524 (1.0)        0.8534 (1.0)         26.3000 (1.0)        0.2010 (1.0)       452;600  37,803.7849 (1.0)        8010           1
test_sqlglot            636.2530 (24.64)    10,335.0290 (226.30)     678.4330 (25.65)    276.6924 (324.21)     653.1080 (24.83)     23.8250 (118.54)      4;225   1,473.9848 (0.04)       1256           1
test_sqlparser        1,563.2770 (60.54)     1,959.0890 (42.90)    1,630.0581 (61.62)     48.6897 (57.05)    1,612.8780 (61.33)     47.4110 (235.89)      63;21     613.4751 (0.02)        537           1
test_mozsqlparser     2,707.5730 (104.86)   11,504.0740 (251.90)   3,053.7567 (115.44)   964.2621 (>1000.0)  2,889.7240 (109.88)   243.1393 (>1000.0)      7;10     327.4655 (0.01)        295           1
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
