benchmark: build
    uvx poetry run pytest tests/benchmark.py

test: 
    uvx poetry run pytest tests/

build:
    uvx poetry build
