.PHONY: help dev build up down logs test clean install

help:
	@echo "TFOCO Financial Document Reader - Available Commands:"
	@echo ""
	@echo "  make dev         - Start development environment"
	@echo "  make build       - Build Docker images"
	@echo "  make up          - Start services"
	@echo "  make down        - Stop services"
	@echo "  make logs        - View logs"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make install     - Install local dependencies"
	@echo ""

dev: build up
	@echo "Development environment started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

build:
	@echo "Building Docker images..."
	docker-compose build

up:
	@echo "Starting services..."
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5

down:
	@echo "Stopping services..."
	docker-compose down

logs:
	docker-compose logs -f

test:
	@echo "Running backend tests..."
	cd backend && pytest -v
	@echo "Tests completed!"

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup completed!"

install:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "Dependencies installed!"

