# Glass Box Portfolio - Development Makefile
#
# Usage:
#   make help          - Show available commands
#   make backend       - Build and run backend in Docker
#   make web           - Run web frontend (development)
#   make dev           - Run both backend and web
#   make clean         - Stop and remove containers

.PHONY: help backend backend-build backend-run backend-stop web dev clean logs test lint

# Default target
help:
	@echo "Glass Box Portfolio - Available Commands"
	@echo "========================================="
	@echo ""
	@echo "Development:"
	@echo "  make dev           - Run both backend (Docker) and web (dev server)"
	@echo "  make backend       - Build and run backend in Docker (port 8080)"
	@echo "  make web           - Run web frontend dev server (port 3000)"
	@echo ""
	@echo "Backend Only:"
	@echo "  make backend-build - Build backend Docker image"
	@echo "  make backend-run   - Run backend container (requires build first)"
	@echo "  make backend-stop  - Stop backend container"
	@echo "  make backend-logs  - Tail backend container logs"
	@echo "  make backend-shell - Open shell in backend container"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run backend tests"
	@echo "  make test-web      - Run web tests"
	@echo "  make lint          - Run linters (backend + web)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Stop containers and clean up"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Docker installed and running"
	@echo "  - Node.js and pnpm installed (for web)"
	@echo "  - backend/.env file with GEMINI_API_KEY set"

# =============================================================================
# Backend (Docker)
# =============================================================================

BACKEND_IMAGE := glass-box-backend
BACKEND_CONTAINER := glass-box-backend
BACKEND_PORT := 8080

backend: backend-build backend-run
	@echo ""
	@echo "Backend is running at http://localhost:$(BACKEND_PORT)"
	@echo "Health check: http://localhost:$(BACKEND_PORT)/health"
	@echo ""
	@echo "To view logs: make backend-logs"
	@echo "To stop: make backend-stop"

backend-build:
	@echo "Building backend Docker image..."
	docker build -t $(BACKEND_IMAGE) ./backend

backend-run: backend-stop
	@echo "Starting backend container..."
	@if [ ! -f backend/.env ]; then \
		echo "ERROR: backend/.env not found!"; \
		echo "Copy backend/.env.example to backend/.env and set GEMINI_API_KEY"; \
		exit 1; \
	fi
	docker run -d \
		--name $(BACKEND_CONTAINER) \
		-p $(BACKEND_PORT):8080 \
		--env-file backend/.env \
		-v $(PWD):/app/codebase:ro \
		-e CODEBASE_ROOT=/app/codebase \
		$(BACKEND_IMAGE)
	@echo "Waiting for backend to start..."
	@sleep 3
	@docker logs $(BACKEND_CONTAINER) --tail 10

backend-stop:
	@docker stop $(BACKEND_CONTAINER) 2>/dev/null || true
	@docker rm $(BACKEND_CONTAINER) 2>/dev/null || true

backend-logs:
	docker logs -f $(BACKEND_CONTAINER)

backend-shell:
	docker exec -it $(BACKEND_CONTAINER) /bin/bash

# =============================================================================
# Web (Development Server)
# =============================================================================

web:
	@echo "Starting web frontend..."
	@echo "Backend URL: http://localhost:$(BACKEND_PORT)"
	cd web && pnpm install && pnpm dev

web-build:
	@echo "Building web frontend..."
	cd web && pnpm install && pnpm build

# =============================================================================
# Development (Both)
# =============================================================================

dev: backend
	@echo ""
	@echo "Starting web frontend in foreground..."
	@echo "Press Ctrl+C to stop web, then 'make backend-stop' to stop backend"
	@echo ""
	cd web && pnpm install && pnpm dev

# =============================================================================
# Testing
# =============================================================================

test:
	@echo "Running backend tests..."
	cd backend && uv run pytest -m "not integration" -v

test-integration:
	@echo "Running integration tests (requires LSP servers)..."
	cd backend && uv run pytest -m "integration" -v

test-web:
	@echo "Running web tests..."
	cd web && pnpm test

test-all: test test-web

# =============================================================================
# Linting
# =============================================================================

lint:
	@echo "Linting backend..."
	cd backend && uv run ruff check app tests
	@echo ""
	@echo "Linting web..."
	cd web && pnpm lint

lint-fix:
	@echo "Fixing backend lint issues..."
	cd backend && uv run ruff check --fix app tests
	@echo ""
	@echo "Fixing web lint issues..."
	cd web && pnpm lint --fix

# =============================================================================
# Cleanup
# =============================================================================

clean: backend-stop
	@echo "Cleaning up..."
	@docker rmi $(BACKEND_IMAGE) 2>/dev/null || true
	@echo "Done."

clean-all: clean
	@echo "Removing all build artifacts..."
	rm -rf backend/.pytest_cache backend/coverage_html backend/.coverage
	rm -rf web/.next web/node_modules/.cache
	@echo "Done."
