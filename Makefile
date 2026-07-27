.PHONY: up down build restart logs ps frontend backend clean

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

clean:
	docker compose down -v