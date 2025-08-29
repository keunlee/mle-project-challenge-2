# Makefile for MLE Project Challenge 2
# House Price Prediction API with Model Watchdog

.PHONY: help dev docker test-unit test-bdd test-watchdog test-all test-comprehensive test-watchdog-with-server lint clean test-multi-reload evaluate

# Default target
help:
	@echo "Available targets:"
	@echo "  dev         - Run API server in development mode"
	@echo "  docker      - Run API server using Docker Compose"
	@echo "  test-unit   - Run unit tests (pytest on tests/unit/)"
	@echo "  test-bdd    - Run behavioral (BDD) tests"
	@echo "  test-watchdog - Test model watchdog functionality"
	@echo "  test-watchdog-with-server - Start server and test watchdog"
	@echo "  test-all    - Run all tests (unit + BDD)"
	@echo "  test-comprehensive - Run all test types (unit + BDD + watchdog + multi-container + evaluation)"
	@echo "  test-multi-reload - Test multi-container hot reloading"
	@echo "  evaluate    - Run comprehensive model evaluation"
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
	@echo "📁 Shared volumes enable hot reloading across containers"
	@echo ""
	docker-compose up -d --build
	@echo ""
	@echo "✅ Services started successfully!"
	@echo "📊 Check status: make docker-status"
	@echo "📋 View logs: make docker-logs"
	@echo "🛑 Stop services: make docker-stop"
	@echo "🧪 Test multi-container reloading: make test-multi-reload"

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

# Watchdog functionality test
test-watchdog:
	@echo "🐕 Testing model watchdog functionality..."
	@echo "📁 Testing automatic model reloading and monitoring"
	@echo "🔧 Using watchdog file monitoring system"
	@echo ""
	@echo "⚠️  Prerequisites:"
	@echo "   - API server must be running (Docker or local)"
	@echo "   - Model watchdog must be enabled"
	@echo "   - Port 8000 must be accessible"
	@echo ""
	@echo "🔍 Checking if API server is running..."
	@if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "✅ API server is running on port 8000"; \
		echo ""; \
		uv run python tools/test_watchdog.py; \
	else \
		echo "❌ API server is not running on port 8000"; \
		echo ""; \
		echo "💡 To start the API server, run one of these commands:"; \
		echo "   make docker     # Start with Docker Compose"; \
		echo "   make dev        # Start development server"; \
		echo ""; \
		echo "Then run: make test-watchdog"; \
		exit 1; \
	fi

# Multi-container hot reloading test
test-multi-reload:
	@echo "🔄 Testing multi-container hot reloading..."
	@echo "📁 Testing shared volume model reloading across containers"
	@echo "🔧 Using enhanced watchdog with container identification"
	@echo ""
	@echo "⚠️  Prerequisites:"
	@echo "   - Docker Compose services must be running"
	@echo "   - Multiple API instances should be active"
	@echo "   - Watchdog must be enabled in all containers"
	@echo ""
	uv run python tools/test_multi_container_reload.py

# Model evaluation target
evaluate:
	@echo "📊 Running comprehensive model evaluation..."
	@echo "🔍 Analyzing model performance and generalization"
	@echo "📈 Generating evaluation metrics and visualizations"
	@echo "📁 Results will be saved to evaluation_results/"
	@echo ""
	uv run python tools/evaluate_model.py
	@echo ""
	@echo "✅ Model evaluation completed!"
	@echo "📊 View results: cat evaluation_results/evaluation_report.txt"
	@echo "🖼️  View visualizations: open evaluation_results/model_evaluation.png"

# Run all tests
test-all: test-unit test-bdd
	@echo ""
	@echo "🎉 All tests completed!"

# Run comprehensive testing (all test types)
test-comprehensive: test-unit test-bdd test-watchdog test-multi-reload evaluate
	@echo ""
	@echo "🎉 Comprehensive testing completed!"
	@echo "✅ Unit tests, BDD tests, watchdog tests, multi-container tests, and model evaluation completed"

# Start API server and test watchdog (convenience target)
test-watchdog-with-server:
	@echo "🚀 Starting API server and testing watchdog..."
	@echo "📁 This will start the server and then run watchdog tests"
	@echo ""
	@echo "Step 1: Starting API server..."
	make docker
	@echo ""
	@echo "Step 2: Waiting for server to be ready..."
	@echo "⏳ Waiting 10 seconds for server to fully start..."
	@sleep 10
	@echo ""
	@echo "Step 3: Testing watchdog functionality..."
	make test-watchdog

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
