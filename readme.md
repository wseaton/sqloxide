
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
```
------------------------------------------------------------------------------------------- benchmark: 3 tests -------------------------------------------------------------------------------------------
Name (time in us)             Min                   Max                  Mean              StdDev                Median                 IQR            Outliers          OPS            Rounds  Iterations
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_sqloxide             32.6160 (1.0)        155.9840 (1.0)         38.2026 (1.0)       12.2385 (1.0)         33.4550 (1.0)        1.1232 (1.0)     2241;3182  26,176.2356 (1.0)       18385           1
test_sqloxide_json        53.6841 (1.65)       195.8520 (1.26)        63.6335 (1.67)      18.8921 (1.54)        55.9980 (1.67)       3.4007 (3.03)     818;1373  15,715.0000 (0.60)       6431           1
test_sqlparser         2,422.7440 (74.28)    8,906.5280 (57.10)    2,743.4912 (71.81)    473.3235 (38.68)    2,643.2245 (79.01)    156.6375 (139.45)      12;28     364.4991 (0.01)        284           1
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

```

## Example:

```
poetry build
poetry run python ./examples/depgraph.py --path {path/to/folder/with/queries} 
```

## TO-DO:
- publish wheels