.PHONY: format lint type-check
format:
	ruff format
lint:
	ruff check --fix
	ruff check --diff
type-check:
	mypy --html-report docs/reports -m sop_chatbot --strict

.PHONY: test test-report debug-tests
test:
	pytest -vvvx tests --cov=sop_chatbot --cov-report=html --durations=5
test-report:
	pytest -vvv tests --cov=sop_chatbot --durations=5 | tee docs/reports/test_results.txt
	coverage html
debug-tests:
	pytest -vvvx tests --cov=sop_chatbot --cov-report=html --durations=5 --pdb

.PHONY: run production-run
run:
	uvicorn sop_chatbot.main:app --host=0.0.0.0 --port=8000 --reload --loop=uvloop
production-run:
	uvicorn sop_chatbot.main:app --host=0.0.0.0 --port=8000 --loop=uvloop --workers=4

.PHONY: dev-tests pre-commit
dev-tests: format lint format type-check test
pre-commit: format lint format type-check test-report 