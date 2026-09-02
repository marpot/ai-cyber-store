.PHONY: up down build restart logs ps frontend backend clean typecheck lint lint-fix test help

help:
	@echo "AI Cyber Store — make targets"
	@echo "  make up            Start all services in background"
	@echo "  make build         Build and start all services"
	@echo "  make down          Stop all services"
	@echo "  make restart       Restart all services"
	@echo "  make logs          Tail logs from all services"
	@echo "  make logs-frontend Tail frontend logs only"
	@echo "  make logs-backend  Tail recommendation-service logs only"
	@echo "  make ps            List running services"
	@echo "  make frontend      Open shell in frontend container"
	@echo "  make backend       Open shell in recommendation-service container"
	@echo "  make typecheck     Run TypeScript type-check (frontend)"
	@echo "  make lint          Run oxlint on the frontend"
	@echo "  make lint-fix      Run oxlint with --fix"
	@echo "  make test          Run frontend typecheck + lint"
	@echo "  make clean         Stop and remove containers + volumes (DESTRUCTIVE)"

up:
	docker compose up -d

build:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-frontend:
	docker compose logs -f frontend

logs-backend:
	docker compose logs -f recommendation-service

ps:
	docker compose ps

frontend:
	docker compose exec frontend sh

backend:
	docker compose exec recommendation-service sh

typecheck:
	cd frontend && npm run typecheck

lint:
	cd frontend && npm run lint

lint-fix:
	cd frontend && npm run lint:fix

test: typecheck lint

clean:
	docker compose down -v