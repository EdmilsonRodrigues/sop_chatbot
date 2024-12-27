.PHONY: lint
lint:
	ruff format
	ruff check --fix
	ruff format

.PHONY: test
test:
	pytest -vvvx tests --cov=sop_chatbot --cov-report=html

.PHONY: pre-commit
pre-commit: lint test