# MemoBot Makefile

.PHONY: help install dev test clean docker-build docker-up docker-down lint format

help: ## Show this help message
	@echo "MemoBot - Memory Layer for Robots"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt
	pip install -e .

dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=backend --cov=sdk --cov-report=html

docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start all services
	docker-compose up -d

docker-down: ## Stop all services
	docker-compose down

docker-logs: ## View logs
	docker-compose logs -f

docker-clean: ## Stop and remove all containers and volumes
	docker-compose down -v

lint: ## Run linters
	flake8 backend/ sdk/ examples/
	black --check backend/ sdk/ examples/

format: ## Format code
	black backend/ sdk/ examples/

clean: ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/

example: ## Run basic example
	python examples/basic_usage.py

example-ros: ## Run ROS integration example
	python examples/ros_integration.py

db-shell: ## Access database shell
	docker-compose exec postgres psql -U postgres -d memobot

redis-shell: ## Access Redis shell
	docker-compose exec redis redis-cli

api-shell: ## Access API container shell
	docker-compose exec api bash

worker-shell: ## Access worker container shell
	docker-compose exec worker bash

scale-workers: ## Scale workers (usage: make scale-workers N=3)
	docker-compose up -d --scale worker=$(N)

logs-api: ## View API logs
	docker-compose logs -f api

logs-worker: ## View worker logs
	docker-compose logs -f worker

restart-api: ## Restart API service
	docker-compose restart api

restart-worker: ## Restart worker service
	docker-compose restart worker

