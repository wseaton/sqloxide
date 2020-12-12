
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
            {
              "UnnamedExpr": {
                "CompoundIdentifier": [
                  {
                    "value": "call",
                    "quote_style": null
                  },
                  {
                    "value": "end_time",
                    "quote_style": null
                  }
                ]
              }
            },
            {
              "UnnamedExpr": {
                "CompoundIdentifier": [
                  {
                    "value": "call_outcome",
                    "quote_style": null
                  },
                  {
                    "value": "outcome_text",
                    "quote_style": null
                  }
                ]
              }
            }
          ],
          "from": [
            {
              "relation": {
                "Table": {
                  "name": [
                    {
                      "value": "employee",
                      "quote_style": null
                    }
                  ],
                  "alias": null,
                  "args": [],
                  "with_hints": []
                }
              },
              "joins": [
                {
                  "relation": {
                    "Table": {
                      "name": [
                        {
                          "value": "call",
                          "quote_style": null
                        }
                      ],
                      "alias": null,
                      "args": [],
                      "with_hints": []
                    }
                  },
                  "join_operator": {
                    "Inner": {
                      "On": {
                        "BinaryOp": {
                          "left": {
                            "CompoundIdentifier": [
                              {
                                "value": "call",
                                "quote_style": null
                              },
                              {
                                "value": "employee_id",
                                "quote_style": null
                              }
                            ]
                          },
                          "op": "Eq",
                          "right": {
                            "CompoundIdentifier": [
                              {
                                "value": "employee",
                                "quote_style": null
                              },
                              {
                                "value": "id",
                                "quote_style": null
                              }
                            ]
                          }
                        }
                      }
                    }
                  }
                },
                {
                  "relation": {
                    "Table": {
                      "name": [
                        {
                          "value": "call_outcome",
                          "quote_style": null
                        }
                      ],
                      "alias": null,
                      "args": [],
                      "with_hints": []
                    }
                  },
                  "join_operator": {
                    "Inner": {
                      "On": {
                        "BinaryOp": {
                          "left": {
                            "CompoundIdentifier": [
                              {
                                "value": "call",
                                "quote_style": null
                              },
                              {
                                "value": "call_outcome_id",
                                "quote_style": null
                              }
                            ]
                          },
                          "op": "Eq",
                          "right": {
                            "CompoundIdentifier": [
                              {
                                "value": "call_outcome",
                                "quote_style": null
                              },
                              {
                                "value": "id",
                                "quote_style": null
                              }
                            ]
                          }
                        }
                      }
                    }
                  }
                }
              ]
            }
          ],
          "selection": null,
          "group_by": [],
          "having": null
        }
      },
      "order_by": [
        {
          "expr": {
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
          },
          "asc": true,
          "nulls_first": null
        }
      ],
      "limit": null,
      "offset": null,
      "fetch": null
    }
  }
]


```
## Benchmarks:

We run 4 seperate benchmarks (on an Intel Skylake, Lenovo P50):

test_sqloxide - get a JSON string back from rust, no serialization back to python dict
test_sqloxide_json - parse in rust + python `json.loads`
test_sqlparser - testing [sqlparse](https://pypi.org/project/sqlparse/), query -> AST
test_mozsqlparser - full roundtrip as in the docs, query -> JSON


```
------------------------------------------------------------------------------------------------ benchmark: 4 tests -----------------------------------------------------------------------------------------------
Name (time in us)              Min                    Max                   Mean                 StdDev                 Median                   IQR            Outliers          OPS            Rounds  Iterations
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_sqloxide              33.6520 (1.0)         145.6850 (1.0)          39.4984 (1.0)          12.3347 (1.0)          34.4590 (1.0)          1.2980 (1.0)     1989;2911  25,317.4531 (1.0)       16013           1
test_sqloxide_json         55.1870 (1.64)        194.4629 (1.33)         68.8028 (1.74)         19.8281 (1.61)         58.0300 (1.68)        16.0275 (12.35)     776;620  14,534.2891 (0.57)       4956           1
test_sqlparser          2,448.9640 (72.77)    10,234.5070 (70.25)     2,833.4313 (71.74)       615.8370 (49.93)     2,703.3210 (78.45)      219.5430 (169.14)      14;21     352.9290 (0.01)        249           1
test_mozsqlparser      13,057.7260 (388.02)   44,944.5860 (308.51)   19,930.3933 (504.59)   10,254.2060 (831.33)   15,520.3370 (450.40)   2,414.8133 (>1000.0)     11;11      50.1746 (0.00)         59           1
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

## Example:

```
poetry build
poetry run python ./examples/depgraph.py --path {path/to/folder/with/queries} 
```

## TO-DO:
- publish wheels