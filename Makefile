.PHONY: run dev test lint clean build

run:
	docker-compose up --build

dev:
	uvicorn backend.main:app --reload --port 8000

test:
	pytest tests/ -v --cov=backend

lint:
	ruff check backend/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build:
	docker-compose build
