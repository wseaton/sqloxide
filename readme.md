
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



## Example:

```
poetry build
poetry run python ./examples/depgraph.py --path {path/to/folder/with/queries} 
```

## TO-DO:
- publish wheels