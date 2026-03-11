.PHONY: install test lint api dashboard

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check src tests dashboard

api:
	uvicorn llm_gateway.api.app:app --reload

dashboard:
	streamlit run dashboard/app.py

