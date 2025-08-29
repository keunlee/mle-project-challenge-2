# Makefile for MLE Project Challenge 2
# House Price Prediction API with Model Watchdog

.PHONY: help dev docker test-unit test-bdd test-all lint clean

# Default target
help:
	@echo "Available targets:"
	@echo "  dev         - Run API server in development mode"
	@echo "  docker      - Run API server using Docker Compose"
	@echo "  test-unit   - Run unit tests"
	@echo "  test-bdd    - Run behavioral (BDD) tests"
	@echo "  test-all    - Run all tests (unit + BDD)"
	@echo "  lint        - Run linting with ruff"
	@echo "  clean       - Clean up temporary files and containers"
	@echo "  help        - Show this help message"

# Development server target
dev:
	@echo "🚀 Starting API server in development mode..."
	@echo "📁 Working directory: $(PWD)"
	@echo "🔧 Using uv for dependency management"
	@echo "👀 Server will be available at: http://localhost:8000"
	@echo "🔄 Auto-reload enabled for development"
	@echo ""
	uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Docker server target
docker:
	@echo "🐳 Starting API server using Docker Compose..."
	@echo "📦 Building and starting services..."
	@echo "🌐 API will be available at: http://localhost:8000"
	@echo "⚖️  Load balancer (nginx) will distribute requests"
	@echo "🔄 Model watchdog is enabled for automatic model reloading"
	@echo ""
	docker-compose up -d --build
	@echo ""
	@echo "✅ Services started successfully!"
	@echo "📊 Check status: make docker-status"
	@echo "📋 View logs: make docker-logs"
	@echo "🛑 Stop services: make docker-stop"

# Docker status check
docker-status:
	@echo "📊 Docker services status:"
	docker-compose ps

# Docker logs
docker-logs:
	@echo "📋 Docker services logs:"
	docker-compose logs -f

# Docker stop
docker-stop:
	@echo "🛑 Stopping Docker services..."
	docker-compose down
	@echo "✅ Services stopped successfully!"

# Unit tests target
test-unit:
	@echo "🧪 Running unit tests..."
	@echo "📁 Test directory: tests/unit/"
	@echo "🔧 Using pytest for test execution"
	@echo ""
	@if [ ! -d "tests/unit" ]; then \
		echo "⚠️  Warning: tests/unit/ directory is empty"; \
		echo "   Create test files in tests/unit/ to run unit tests"; \
		echo "   Example: tests/unit/test_model_service.py"; \
		exit 0; \
	fi
	uv run pytest tests/unit/ -v --tb=short

# BDD tests target
test-bdd:
	@echo "🌱 Running behavioral (BDD) tests..."
	@echo "📁 Test directory: tests/bdd/"
	@echo "🔧 Using pytest-bdd for behavior-driven development"
	@echo ""
	@if [ ! -d "tests/bdd" ]; then \
		echo "⚠️  Warning: tests/bdd/ directory is empty"; \
		echo "   Create BDD test files in tests/bdd/ to run behavioral tests"; \
		echo "   Example: tests/bdd/test_api_behavior.py"; \
		exit 0; \
	fi
	uv run pytest tests/bdd/ -v --tb=short

# Run all tests
test-all: test-unit test-bdd
	@echo ""
	@echo "🎉 All tests completed!"

# Linting target using ruff
lint:
	@echo "🔍 Running linting with ruff..."
	@echo "📁 Checking source code in src/"
	@echo "📁 Checking test code in tests/"
	@echo "📁 Checking tools in tools/"
	@echo ""
	uv run ruff check src/ tests/ tools/
	@echo ""
	@echo "✅ Linting completed!"

# Format code using ruff
format:
	@echo "✨ Formatting code with ruff..."
	@echo "📁 Formatting source code in src/"
	@echo "📁 Formatting test code in tests/"
	@echo "📁 Formatting tools in tools/"
	@echo ""
	uv run ruff format src/ tests/ tools/
	@echo ""
	@echo "✅ Code formatting completed!"

# Clean target
clean:
	@echo "🧹 Cleaning up temporary files and containers..."
	@echo "🛑 Stopping Docker services..."
	-docker-compose down
	@echo "🗑️  Removing temporary files..."
	-find . -type f -name "*.pyc" -delete
	-find . -type d -name "__pycache__" -delete
	-find . -type f -name "*.pyo" -delete
	-find . -type f -name "*.pyd" -delete
	-find . -type f -name ".coverage" -delete
	-find . -type d -name ".pytest_cache" -delete
	-find . -type d -name ".ruff_cache" -delete
	@echo "✅ Cleanup completed!"

# Install development dependencies
install-dev:
	@echo "📦 Installing development dependencies..."
	@echo "🔧 Installing pytest, pytest-bdd, and ruff..."
	uv add --dev pytest pytest-bdd ruff
	@echo "✅ Development dependencies installed!"

# Show project status
status:
	@echo "📊 Project Status:"
	@echo "=================="
	@echo "🐳 Docker services:"
	@docker-compose ps 2>/dev/null || echo "   No Docker services running"
	@echo ""
	@echo "📁 Test structure:"
	@echo "   Unit tests: tests/unit/ ($(shell find tests/unit -name "*.py" | wc -l) files)"
	@echo "   BDD tests: tests/bdd/ ($(shell find tests/bdd -name "*.py" | wc -l) files)"
	@echo ""
	@echo "🔧 Dependencies:"
	@echo "   Development tools: $(shell uv list --dev 2>/dev/null | grep -E "(pytest|ruff)" | wc -l) installed"
	@echo ""
	@echo "📋 Available targets: make help"
