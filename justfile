dev:
    uv sync
    uv run maturin develop --release

check: dev
    uv run ty check tests/test_sqloxide.py tests/test_stubs.py

test: dev
    uv run pytest tests/test_sqloxide.py -v

benchmark: dev
    uv run pytest tests/benchmark.py
