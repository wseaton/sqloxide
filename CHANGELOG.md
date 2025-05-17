# 0.1.56

- Upgrade to sqlparser-rs 0.56.0

In v0.55 of sqlparser-rs, the `ObjectName` structure has been changed as shown below. Here is now to migrate.

```diff
- pub struct ObjectName(pub Vec<Ident>);
+ pub struct ObjectName(pub Vec<ObjectNamePart>)
```

Therefore, when using the `parse_sql` function, the data structure of the table name in the return value will change.

Previously:

```json
{
    "value": "employee",
    "quote_style": null,
    "span":
    {
        "start":
        {
            "line": 4,
            "column": 10
        },
        "end":
        {
            "line": 4,
            "column": 18
        }
    }
}
```

Now:


```json
{
    "Identifier":
    {
        "value": "employee",
        "quote_style": null,
        "span":
        {
            "start":
            {
                "line": 4,
                "column": 10
            },
            "end":
            {
                "line": 4,
                "column": 18
            }
        }
    }
}
```

# 0.1.36

- Upgrade to sqlparser-rs 0.36.0
- Add more visitor functions
  - `mutate_relations`
  - `mutate_expressions`
  - `extract_expressions`
- add `restore_ast`
- remove ability for library to internally panic via `.expect()`, now throws only `ValueError`

# 0.1.35

- Added `extract_relations` function to assist in extracting table references from the AST in Rust.
