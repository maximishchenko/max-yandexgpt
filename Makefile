.PHONY: lint-all typing-all tests-all check-all \
        lint-file typing-file test-file check-file \
        pre-commit sync check-commit-msg coverage \
		version version-dry-run install-hooks

check-all: lint-all typing-all tests-all coverage

check-file: lint-file typing-file test-file coverage

lint-all:
	uv run ruff check max_yandexgpt

typing-all:
	uv run --with mypy -- python -m mypy --strict max_yandexgpt

tests-all:
	uv run pytest -v

lint-file:
	uv run ruff check --force-exclude $(FILE)

typing-file:
	uv run --with mypy -- python -m mypy --strict $(FILE)

test-file:
	uv run pytest -v $(FILE)

pre-commit:
	uv run python -m pre_commit run --all-files

check-commit-msg:
	uv run python -m commitizen check --commit-msg-file $(filter-out $@,$(MAKECMDGOALS))

coverage:
	uv run python -m coverage run -m pytest
	uv run python -m coverage report

version:
	uv run python -m commitizen bump

version-dry-run:
	uv run python -m commitizen bump --dry-run --yes

install-hooks:
	uv run python -m pre_commit install
	uv run python -m pre_commit install --hook-type commit-msg
	uv run python -m pre_commit install --hook-type post-commit

run-bot:
	powershell -ExecutionPolicy Bypass -File "./setup_env.ps1"
	uv run bot.py

%:
	@:

sync:
	uv sync
