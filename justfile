benchmark:
    uv sync
    uv run maturin develop --release
    uv run pytest tests/benchmark.py

test:
    uv sync
    uv run maturin develop
    uv run pytest tests/

build:
    uv run maturin build --release
