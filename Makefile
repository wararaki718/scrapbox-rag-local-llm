.PHONY: setup help up down build ps logs backend-shell frontend-shell test lint format

# Variables
DC = docker compose
BACKEND_DIR = backend
FRONTEND_DIR = frontend

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  setup           Initialize project (install hooks, etc.)"
	@echo "  up              Start all services in background"
	@echo "  down            Stop all services"
	@echo "  build           Build or rebuild services"
	@echo "  ps              List containers"
	@echo "  logs            Follow logs from all containers"
	@echo "  test            Run all tests (backend & frontend)"
	@echo "  lint            Run linters"
	@echo "  format          Run formatters"
	@echo "  backend-shell   Enter backend container shell"
	@echo "  frontend-shell  Enter frontend container shell"
	@echo "  import JSON=path/to/file.json  Import Scrapbox data from JSON file"

setup:
	@echo "Setting up project..."
	cd $(BACKEND_DIR) && uv sync
	cd $(FRONTEND_DIR) && npm install

up:
	$(DC) up -d

down:
	$(DC) down

build:
	$(DC) build

ps:
	$(DC) ps

logs:
	$(DC) logs -f

test: test-backend test-frontend

test-backend:
	@echo "Running backend tests..."
	$(DC) exec backend uv run pytest

test-frontend:
	@echo "Running frontend tests..."
	$(DC) exec frontend npm test

lint: lint-backend lint-frontend

lint-backend:
	@echo "Running backend lint (ruff)..."
	$(DC) exec backend uv run ruff check .

lint-frontend:
	@echo "Running frontend lint (eslint)..."
	$(DC) exec frontend npm run lint

format: format-backend format-frontend

format-backend:
	@echo "Formatting backend code (ruff)..."
	$(DC) exec backend uv run ruff format .

format-frontend:
	@echo "Formatting frontend code (prettier)..."
	$(DC) exec frontend npm run format || echo "Format script not found, skipping..."

backend-shell:
	$(DC) exec backend /bin/bash

frontend-shell:
	$(DC) exec frontend /bin/sh

import:
	@if [ -n "$(JSON)" ]; then \
		cp $(JSON) backend/temp_import.json; \
		$(DC) exec backend uv run python scripts/import_scrapbox.py --json temp_import.json; \
		rm backend/temp_import.json; \
	elif [ -n "$(PROJECT)" ]; then \
		$(DC) exec backend uv run python scripts/import_scrapbox.py --project $(PROJECT) $(if $(SID),--sid $(SID)); \
	else \
		echo "Error: Either JSON or PROJECT variable is required."; \
		echo "Usage (File): make import JSON=data.json"; \
		echo "Usage (API):  make import PROJECT=my-project [SID=connect.sid]"; \
		exit 1; \
	fi
