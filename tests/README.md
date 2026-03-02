# Comp430 - Chimps Compiler

A compiler for the Chimps programming language, built in Python.

## Requirements

- Python 3.12+


## Install Dependencies

```
pip3 install pytest pytest-cov
```


## Running Tests

Run all unit tests:

```
pytest
```

Run tests with coverage report:

```
pytest --cov=src
```

Run tests with detailed HTML coverage report:

```
pytest --cov=src --cov-report=html
```

Then open `htmlcov/index.html` in your browser to view the report.
