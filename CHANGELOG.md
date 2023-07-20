
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
