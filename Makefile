.PHONY: help install format lint test coverage clean up down restart build seed logs shell

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies and pre-commit hooks"
	@echo "  make format     - Format code with black and isort"
	@echo "  make lint       - Run flake8 linter"
	@echo "  make test       - Run tests"
	@echo "  make coverage   - Run tests with coverage report"
	@echo "  make build      - Build Docker containers"
	@echo "  make up         - Start Docker containers"
	@echo "  make down       - Stop Docker containers"
	@echo "  make restart    - Restart Docker containers"
	@echo "  make seed       - Seed database with demo data"
	@echo "  make logs       - Show API logs"
	@echo "  make shell      - Open shell in API container"
	@echo "  make clean      - Remove cache and temporary files"
	@echo "  make reset      - Full reset (down, clean volumes, up)"

install:
	pip install -r requirements.txt
	pre-commit install

format:
	black app/
	isort app/

lint:
	flake8 app/

test:
	docker compose exec api pytest app/tests/ -v

coverage:
	docker compose exec api pytest app/tests/ --cov=app --cov-report=html --cov-report=term-missing

build:
	docker compose build

up:
	docker compose up -d
	@echo "🚀 Application starting..."
	@echo "📝 Swagger UI: http://localhost:8000/docs"
	@echo "🏥 Health check: http://localhost:8000/health"

down:
	docker compose down

restart:
	docker compose restart api

seed:
	docker compose exec api python scripts/seed_data.py

logs:
	docker compose logs -f api

shell:
	docker compose exec api bash

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/

reset:
	docker compose down -v
	docker volume prune -f
	docker compose up -d --build
	@echo "🔄 Full reset complete!"
