# Makefile for AI-Powered Playwright Test Generator
# Works on Windows with make or nmake

.PHONY: help install install-dev test test-unit test-integration test-parallel \
        coverage lint format clean generate-tests run-demo

# Default target
help:
	@echo "AI-Powered Playwright Test Generator - Available Commands:"
	@echo ""
	@echo "  make install        - Install production dependencies"
	@echo "  make install-dev    - Install all dependencies including dev/test"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-parallel - Run tests in parallel"
	@echo "  make coverage      - Run tests with coverage report"
	@echo "  make lint          - Run linters (flake8, mypy, pylint)"
	@echo "  make format        - Format code with black and isort"
	@echo "  make clean         - Clean up generated files"
	@echo "  make generate-tests - Generate tests for a URL"
	@echo "  make run-demo      - Run the AI generation demo"

# Installation targets
install:
	pip install -r requirements.txt
	pip install -r requirements-ai.txt
	playwright install chromium firefox webkit

install-dev: install
	pip install -r requirements-test.txt

# Testing targets
test:
	python run_tests.py

test-unit:
	python run_tests.py --type unit

test-integration:
	python run_tests.py --type integration

test-parallel:
	python run_tests.py --parallel

coverage:
	python run_tests.py
	@echo "Opening coverage report..."
	start htmlcov/index.html

# Code quality targets
lint:
	flake8 src tests --max-line-length=100 --ignore=E203,W503
	mypy src --ignore-missing-imports
	pylint src --disable=C0111,R0903

format:
	black src tests --line-length=100
	isort src tests --profile=black

# Cleaning targets
clean:
	@echo "Cleaning up generated files..."
	if exist "__pycache__" rmdir /s /q __pycache__
	if exist ".pytest_cache" rmdir /s /q .pytest_cache
	if exist "htmlcov" rmdir /s /q htmlcov
	if exist ".coverage" del .coverage
	if exist "coverage.xml" del coverage.xml
	if exist "reports" rmdir /s /q reports
	for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

# Generation targets
generate-tests:
	@echo "Generating tests for localhost..."
	python run.bat --url http://localhost:5173 --username admin@example.com --password admin123 --mode generate --output-dir ./generated_tests

run-demo:
	python demo_ai_generation.py

# Development helpers
check: lint test
	@echo "All checks passed!"

setup: install-dev
	@echo "Development environment ready!"

# CI/CD helpers
ci: install-dev lint test
	@echo "CI checks completed!"

# Documentation
docs:
	@echo "Opening documentation..."
	start AI_PROVIDERS_README.md
	start CONFIG.md