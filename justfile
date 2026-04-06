dev:
    uv sync
    uv run maturin develop --release

test: dev
    uv run pytest tests/test_sqloxide.py -v

benchmark: dev
    uv run pytest tests/benchmark.py
