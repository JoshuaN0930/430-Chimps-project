# Comp430 - Chimps Compiler

A compiler for the Chimps programming language, built in Python.

## Requirements

- Python 3.12+

## Setup

Clone the repository and navigate to the project root:

```
git clone https://github.com/JoshuaN0930/430-Chimps-project.git
cd 430-Chimps-project
```

## Install Dependencies

```
pip3 install pytest pytest-cov
```

## Running the Compiler

Run a Chimps source file:

```
python3 main.py test.chimps
```

Or use the interactive terminal prompt:

```
python3 main.py
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
