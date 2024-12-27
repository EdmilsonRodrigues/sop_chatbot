.PHONY: lint
lint:
	ruff check --fix
	ruff format

.PHONY: test
test:
	pytest -vvvx tests --cov=sop_chatbot --cov-report=html
