.PHONY: format lint type-check
format:
	uv run ruff format
lint:
	uv run ruff check --fix
	uv run ruff check --diff
type-check:
	uv run mypy --html-report docs/reports -m sop_chatbot --strict

.PHONY: test test-report debug-tests ci-tests
test:
	uv run pytest -vvvx tests --cov=sop_chatbot --cov-report=html --durations=5
test-report:
	uv run pytest -vvv tests --cov=sop_chatbot --durations=5 | tee docs/reports/test_results.txt
	uv run coverage html
debug-tests:
	uv run pytest -vvvx tests --cov=sop_chatbot --cov-report=html --durations=5 --pdb
ci-tests:
	uv run pytest -vvv tests


.PHONY: run production-run
run:
	uv run uvicorn sop_chatbot.main:app --host=0.0.0.0 --port=8000 --reload --loop=uvloop
production-run:
	uv run uvicorn sop_chatbot.main:app --host=0.0.0.0 --port=8000 --loop=uvloop --workers=4

.PHONY: dev-tests pre-commit
dev-tests: format lint format type-check test
pre-commit: format lint format type-check test-report 
