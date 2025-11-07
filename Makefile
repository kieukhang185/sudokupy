.PHONY: up down logs api frontend fmt

up:
	docker compose -f infra/docker-compose.yml --project-directory . up --build
down:
	docker compose -f infra/docker-compose.yml --project-directory . down
logs:
	docker compose -f infra/docker-compose.yml --project-directory . logs -f

api:
	cd api && uvicorn app.main:app --reload
frontend:
	cd frontend && npm run dev

fmt:
	pre-commit run --all-files || true