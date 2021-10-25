benchmark: build
    poetry run pytest tests/benchmark.py

test: 
    poetry run pytest tests/benchmark.py

build:
    poetry build