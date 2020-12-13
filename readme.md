
# sqloxide

This project wraps rust bindings for [sqlparser-rs](https://github.com/ballista-compute/sqlparser-rs) into a python package.


## Usage:

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
## Benchmarks:

We run 3 seperate benchmarks:

* `test_sqloxide` - parse query and get a python object back from rust 
* `test_sqlparser` - testing [sqlparse](https://pypi.org/project/sqlparse/), query -> AST
* `test_mozsqlparser` - full roundtrip as in the docs, query -> JSON

```
poetry run pytest tests/benchmark.py
```

```
----------------------------------------------------------------------------------------------- benchmark: 3 tests -----------------------------------------------------------------------------------------------
Name (time in us)             Min                    Max                   Mean                 StdDev                 Median                   IQR            Outliers          OPS            Rounds  Iterations
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_sqloxide             38.1560 (1.0)          77.6420 (1.0)          39.1003 (1.0)           1.8152 (1.0)          38.7980 (1.0)          0.2990 (1.0)       395;615  25,575.2524 (1.0)        7712           1
test_sqlparser         2,012.0290 (52.73)     9,291.2800 (119.67)    2,126.9194 (54.40)       406.3374 (223.85)    2,061.9015 (53.14)       72.8010 (243.47)       9;27     470.1636 (0.02)        398           1
test_mozsqlparser     10,825.9870 (283.73)   46,720.8870 (601.75)   18,024.9295 (460.99)   10,937.3574 (>1000.0)  13,128.5660 (338.38)   3,099.9100 (>1000.0)     13;13      55.4787 (0.00)         64           1
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

## Example:

The `depgraph` example reads a bunch of `.sql` files from disk using glob, and builds a dependency graph of all of the objects using graphviz.

```
poetry run python ./examples/depgraph.py --path {path/to/folder/with/queries} 
```

## Develop

1) Install `rustup`

2) `poetry install` will automatically create the venv, compile the package and install it into the venv via the build script.

## TO-DO:
- publish wheels