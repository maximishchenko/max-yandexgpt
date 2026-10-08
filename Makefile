UV := uv run

# Docker environment: make docker-up APP_ENV=production  (or ENV=prod).
# Selects docker/<APP_ENV>/bot.override.yml. Default: development.
ifeq ($(ENV),prod)
APP_ENV := production
endif
APP_ENV ?= development
export APP_ENV

# FILE=path/to/file.py for the *-file targets, MSG=path for check-commit-msg.
FILE ?=
MSG ?= .git/COMMIT_EDITMSG
require-file = $(if $(FILE),,$(error FILE is required, e.g. make $@ FILE=max_yandexgpt/bot.py))

.DEFAULT_GOAL := help

.PHONY: help sync \
        lint-all typing-all tests-all coverage check-all \
        lint-file typing-file test-file check-file \
        format clean \
        pre-commit install-hooks check-commit-msg \
        version version-dry-run freeze \
        init up down pull restart rebuild \
        docker-up docker-build docker-down docker-pull docker-logs \
        docker-tools-build docker-lint docker-typing docker-tests \
        docker-coverage docker-check docker-init-secrets

help: ## Show this help
	@$(UV) python -c "import re; [print(f'  {m[1]:<20} {m[2]}') for m in re.finditer(r'^([\w-]+):.*?## (.*)$$', open('Makefile', encoding='utf-8').read(), re.M)]"

# --- Development ---

sync: ## Install dependencies
	uv sync

lint-all: ## Ruff check
	$(UV) ruff check max_yandexgpt

typing-all: ## Mypy strict check
	$(UV) mypy --strict max_yandexgpt

tests-all: ## Run tests
	$(UV) pytest -v

coverage: ## Run tests with coverage report
	$(UV) coverage run -m pytest
	$(UV) coverage report

check-all: lint-all typing-all coverage ## Lint, typing, tests with coverage

lint-file: ## Ruff check one file (FILE=...)
	$(require-file)
	$(UV) ruff check --force-exclude $(FILE)

typing-file: ## Mypy one file (FILE=...)
	$(require-file)
	$(UV) mypy --strict $(FILE)

test-file: ## Run tests of one file (FILE=...)
	$(require-file)
	$(UV) pytest -v $(FILE)

check-file: lint-file typing-file test-file ## Lint, typing, tests for one file (FILE=...)

format: ## Ruff format
	$(UV) ruff format max_yandexgpt tests

clean: ## Remove caches and coverage data
	$(UV) python -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in map(pathlib.Path, ['.mypy_cache', '.pytest_cache', '.ruff_cache', 'htmlcov'])]; pathlib.Path('.coverage').unlink(missing_ok=True)"

# --- Git hooks / releases ---

pre-commit: ## Run pre-commit on all files
	$(UV) pre-commit run --all-files

install-hooks: ## Install git hooks
	$(UV) pre-commit install
	$(UV) pre-commit install --hook-type commit-msg
	$(UV) pre-commit install --hook-type post-commit

check-commit-msg: ## Check commit message (MSG=.git/COMMIT_EDITMSG)
	$(UV) cz check --commit-msg-file $(MSG)

version: ## Bump version
	$(UV) cz bump

version-dry-run: ## Preview next version
	$(UV) cz bump --dry-run --yes

freeze: ## Export requirements.txt (+ requirements-dev.txt with ENV=dev)
	uv export --no-dev --no-hashes --no-emit-project -o requirements.txt
ifeq ($(ENV),dev)
	uv export --only-dev --no-hashes --no-emit-project -o requirements-dev.txt
endif

# --- Docker ---

init: docker-down docker-build docker-up ## Recreate and start containers
up: docker-up
down: docker-down
pull: docker-pull
restart: docker-down docker-up ## Restart containers
rebuild: docker-down docker-build docker-up ## Rebuild images and restart

docker-up: ## Start containers
	docker compose up -d

docker-build: ## Build images (pulls newer base images)
	docker compose build --pull

docker-down: ## Stop and remove containers
	docker compose down --remove-orphans

docker-pull: ## Pull images
	docker compose pull

docker-logs: ## Follow logs
	docker compose logs -f --tail=100

# --- Checks inside a container (alpine, dev dependencies, source as volume) ---

DOCKER_TOOLS := docker compose run --rm tools

docker-tools-build: ## Build the tools image (after changing dependencies)
	docker compose build tools

docker-lint: ## Ruff check in a container
	$(DOCKER_TOOLS) ruff check max_yandexgpt

docker-typing: ## Mypy strict check in a container
	$(DOCKER_TOOLS) mypy --strict max_yandexgpt

docker-tests: ## Run tests in a container
	$(DOCKER_TOOLS) pytest -v

docker-coverage: ## Run tests with coverage report in a container
	$(DOCKER_TOOLS) sh -c "coverage run -m pytest && coverage report"

docker-check: docker-lint docker-typing docker-coverage ## Lint, typing, tests with coverage in a container

docker-init-secrets: ## Create secret files (development only)
ifeq ($(APP_ENV),development)
	docker compose --profile init run --rm init-secrets
else
	@echo "Secrets generation for $(APP_ENV) environment is disabled."
endif
