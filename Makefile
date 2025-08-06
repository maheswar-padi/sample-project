.PHONY: help install install-dev test test-cov lint format type-check security clean build docs serve-docs pre-commit quality all

# Default target
help:
	@echo "Available commands:"
	@echo "  install       Install production dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage report"
	@echo "  lint          Run linting (flake8)"
	@echo "  format        Format code (black, isort)"
	@echo "  type-check    Run type checking (mypy)"
	@echo "  security      Run security checks (bandit, safety)"
	@echo "  pre-commit    Install and run pre-commit hooks"
	@echo "  quality       Run all quality checks (lint, format, type-check)"
	@echo "  clean         Clean build artifacts and cache files"
	@echo "  build         Build package"
	@echo "  docs          Build documentation"
	@echo "  serve-docs    Serve documentation locally"
	@echo "  all           Run quality checks, tests, and build"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

# Testing
test:
	pytest

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml

test-watch:
	pytest-watch -- --cov=src

# Code quality
lint:
	flake8 src/ tests/

format:
	black src/ tests/
	isort src/ tests/

format-check:
	black --check src/ tests/
	isort --check-only src/ tests/

type-check:
	mypy src/

# Security
security:
	bandit -r src/
	safety check

# Pre-commit
pre-commit-install:
	pre-commit install

pre-commit:
	pre-commit run --all-files

# Combined quality checks
quality: lint format-check type-check
	@echo "All quality checks passed!"

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Building
build: clean
	python -m build

build-check: build
	twine check dist/*

# Documentation
docs:
	@echo "Documentation build not configured yet"
	@echo "Consider adding Sphinx or MkDocs configuration"

serve-docs:
	@echo "Documentation serving not configured yet"

# Development server/demo
demo:
	@echo "Creating demo files..."
	@mkdir -p demo-files
	@echo "This is a sample document for demonstration." > demo-files/sample1.txt
	@echo "Another document with different content and multiple sentences. It has various words and punctuation!" > demo-files/sample2.txt
	@echo "Final demo document with numbers like 123 and 456." > demo-files/sample3.txt
	@echo "Demo files created in demo-files/"
	@echo ""
	@echo "Try these commands:"
	@echo "  textprocessor analyze demo-files/sample1.txt"
	@echo "  textprocessor transform demo-files/sample1.txt --operation upper --no-backup"
	@echo "  textprocessor batch-analyze demo-files/*.txt --format json"

# Complete workflow
all: quality test build
	@echo "All checks passed and package built successfully!"

# Release helpers
release-check: all
	@echo "Release checks complete!"
	@echo "Ready for release if all tests passed."

# Environment setup
setup-dev: install-dev pre-commit-install
	@echo "Development environment setup complete!"
	@echo "Run 'make demo' to create sample files for testing."

# Quick development cycle
dev: format lint test
	@echo "Development cycle complete!"

# CI simulation (run what CI runs)
ci: quality test-cov security build
	@echo "CI simulation complete!"