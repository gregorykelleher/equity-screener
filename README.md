# Screener

A Streamlit application for financial data analysis and visualisation.

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```sh
uv venv --python 3.12
uv sync --all-packages
```

## Run

```sh
uv run streamlit run packages/streamlit-app/src/streamlit_app/main.py
```

## Development

Format and lint:

```sh
uv run ruff format
uv run ruff check
```
