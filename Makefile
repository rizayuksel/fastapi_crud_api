.PHONY: help install format lint test clean up down seed logs

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies and pre-commit hooks"
	@echo "  make format     - Format code with black and isort"
	@echo "  make lint       - Run flake8 linter"
	@echo "  make test       - Run tests with coverage"
	@echo "  make up         - Start Docker containers"
	@echo "  make down       - Stop Docker containers"
	@echo "  make seed       - Seed database with demo data"
	@echo "  make logs       - Show API logs"
	@echo "  make clean      - Remove cache and temporary files"

install:
	pip install -r requirements.txt
	pre-commit install

format:
	black app/
	isort app/

lint:
	flake8 app/

test:
	docker compose exec api pytest --cov=app --cov-report=html --cov-report=term

up:
	docker compose up -d
	@echo "🚀 Application starting..."
	@echo "📝 Swagger UI: http://localhost:8000/docs"
	@echo "🏥 Health check: http://localhost:8000/health"

down:
	docker compose down

seed:
	docker compose exec api python scripts/seed_data.py

logs:
	docker compose logs -f api

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
