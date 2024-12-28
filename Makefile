.PHONY: lint
lint:
	ruff format
	ruff check --fix
	ruff format
	mypy --html-report docs/reports -m sop_chatbot

.PHONY: test
test:
	pytest -vvvx tests --cov=sop_chatbot --cov-report=html --durations=5 | tee docs/reports/test_results.txt

.PHONY: debug-tests
debug-tests:
	pytest -vvvx tests --cov=sop_chatbot --cov-report=html --durations=5 --pdb



.PHONY: pre-commit
pre-commit: lint test