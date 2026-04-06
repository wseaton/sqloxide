# 0.61.0

- upgrade to sqlparser-rs 0.61.0, pyo3 0.28, pythonize 0.28
- add free-threaded python (3.13t, 3.14t) wheel builds
- add python 3.14 support
- drop python 3.7 and 3.8 (EOL, incompatible with pyo3 0.28)
- new versioning scheme: minor version now tracks sqlparser-rs minor (e.g. sqloxide 0.61.0 wraps sqlparser 0.61)
- switch dev tooling from poetry to uv
- version is now sourced from Cargo.toml only (`dynamic` in pyproject.toml)

### breaking changes from sqlparser-rs 0.57-0.61

- several `Statement` variants (e.g. `Update`, `CreateView`, `Truncate`, `Grant`, `Revoke`) changed from inline struct variants to tuple-struct wrappers. the serde/JSON shape of these statements will differ from 0.1.56.
- `ObjectNamePart` now has a `Function` variant in addition to `Identifier` (snowflake `IDENTIFIER(...)` support)
- table alias rendering dropped the explicit `AS` keyword (e.g. `JOIN t AS a` now renders as `JOIN t a`)

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
