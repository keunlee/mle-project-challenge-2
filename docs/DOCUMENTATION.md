# phData Machine Learning Engineer Project - Comprehensive Documentation

A production-ready machine learning solution that provides a scalable RESTful API for predicting house prices using a K-Nearest Neighbors model with automatic demographic data enrichment and horizontal scaling capabilities.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [1. Set up the environment](#1-set-up-the-environment)
  - [2. Train the model](#2-train-the-model)
  - [3. Start the API service](#3-start-the-api-service)
  - [4. Test the API](#4-test-the-api)
  - [5. Evaluate the model](#5-evaluate-the-model)
- [API Endpoints](#api-endpoints)
  - [Base URL](#base-url-httplocalhost8000-via-nginx-load-balancer)
  - [Full Features Endpoint](#full-features-endpoint)
  - [Minimal Features Endpoint](#minimal-features-endpoint)
  - [Response Format](#response-format)
- [Docker Deployment](#docker-deployment)
  - [Multi-Service with Load Balancing and Scaling](#multi-service-with-load-balancing-and-scaling)
  - [Architecture Components](#architecture-components)
  - [Scaling Configuration](#scaling-configuration)
- [Model Evaluation](#model-evaluation)
  - [Automated Evaluation](#automated-evaluation)
  - [Evaluation Metrics](#evaluation-metrics)
  - [Performance Analysis](#performance-analysis)
- [Scaling and Deployment Features](#scaling-and-deployment-features)
  - [Horizontal Scaling](#horizontal-scaling)
  - [Zero-Downtime Deployments](#zero-downtime-deployments)
  - [Auto-scaling Considerations](#auto-scaling-considerations)
- [Testing](#testing)
  - [API Testing](#api-testing)
  - [Model Testing](#model-testing)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Docker Configuration](#docker-configuration)
  - [Nginx Configuration](#nginx-configuration)
- [Performance Considerations](#performance-considerations)
  - [Optimization Features](#optimization-features)
  - [Monitoring](#monitoring)
- [Error Handling](#error-handling)
- [Security Considerations](#security-considerations)
- [Development](#development)
  - [Adding New Features](#adding-new-features)
  - [Model Updates](#model-updates)
- [Deliverable Requirements Compliance](#deliverable-requirements-compliance)
  - [Requirement 1: RESTful API Endpoint](#requirement-1-restful-api-endpoint)
  - [Requirement 2: Test Script](#requirement-2-test-script)
  - [Requirement 3: Model Evaluation](#requirement-3-model-evaluation)
- [Production Deployment](#production-deployment)
  - [Scaling Commands](#scaling-commands)
  - [Monitoring](#monitoring-1)
  - [Load Testing](#load-testing)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)
- [Success Metrics](#success-metrics)

## Project Overview

This project addresses the real-world business need of Sound Realty, a Seattle-based real estate company that wants to streamline their property valuation process using machine learning. The solution provides:

- **Automated house price predictions** using ML models
- **Demographic data enrichment** from ZIP codes
- **Scalable REST API** with load balancing
- **Zero-downtime deployments** and model updates
- **Comprehensive testing** and evaluation tools

## Architecture Overview

This solution implements a production-ready, horizontally scalable API service that:

- **Automatically enriches** house data with demographic information from ZIP codes
- **Provides two endpoints**: full-feature and minimal-feature prediction
- **Scales horizontally** using Docker containers with nginx load balancing
- **Includes comprehensive testing** and model evaluation tools
- **Supports zero-downtime deployments** and model updates
- **Uses modern containerization** with Docker Compose and uv package management

## Project Structure

```
mle-project-challenge-2/
├── data/                          # Data files
│   ├── kc_house_data.csv         # House sales data for training
│   ├── zipcode_demographics.csv  # ZIP code demographics
│   └── future_unseen_examples.csv # Test examples for predictions
├── model/                         # Model artifacts (generated)
│   ├── model.pkl                 # Trained model
│   └── model_features.json       # Feature list and order
├── src/                          # Source code
│   ├── main.py                   # FastAPI application entry point
│   ├── core/                     # Core functionality
│   │   ├── dependencies.py       # Dependency injection
│   │   ├── logging_config.py     # Logging configuration
│   │   └── model_watchdog.py     # Model monitoring
│   ├── models/                   # Data models
│   │   └── requests.py           # Pydantic request models
│   ├── routers/                  # API route handlers
│   │   ├── basic_router.py       # Health and info endpoints
│   │   └── model_router.py       # Prediction endpoints
│   └── services/                 # Business logic
│       └── model_service.py      # Model prediction service
├── tools/                        # Development and testing tools
│   ├── evaluate_model.py         # Model evaluation script
│   └── test_api.py               # API testing script
├── evaluation_results/            # Model evaluation outputs
│   ├── evaluation_report.txt     # Text evaluation report
│   └── model_evaluation.png      # Performance visualization
├── Dockerfile                     # Container configuration
├── docker-compose.yml             # Multi-service deployment with scaling
├── nginx.conf                     # Load balancer configuration
├── pyproject.toml                 # Project configuration and dependencies
├── uv.lock                        # Locked dependency versions
├── conda_environment.yml          # Conda environment (alternative)
├── create_model.py                # Model training script
└── README.md                      # Project overview and requirements
```

## Quick Start

### Prerequisites

- **Docker and Docker Compose** (recommended for production deployment)
- **Python 3.11+** (for local development)
- **uv** (modern Python package manager) or **Conda**

### 1. Set up the environment

#### Option A: Using uv (Recommended)
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

#### Option B: Using Conda
```bash
conda env create -f conda_environment.yml
conda activate housing
```

### 2. Train the model

```bash
# Using UV
uv run create_model.py

# Using Conda
python create_model.py
```

This will create the `model/` directory with the trained model and feature list.

### 3. Start the API service

#### Option A: Docker Compose (Production - Recommended)
```bash
# Start with 3 API instances and nginx load balancer
docker-compose up -d

# Scale to more instances if needed
docker-compose up -d --scale mle-api=5
```

#### Option B: Local Development
```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Test the API

```bash
# Test the load-balanced API
curl http://localhost:8000/health

# Run comprehensive tests
uv run python tools/test_api.py
```

### 5. Evaluate the model

```bash
# Run model evaluation
uv run python tools/evaluate_model.py

# View results
cat evaluation_results/evaluation_report.txt
```

## API Endpoints

### Base URL: `http://localhost:8000` (via nginx load balancer)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/health` | GET | Health check endpoint |
| `/model-info` | GET | Model information and features |
| `/predict/full` | POST | Full-feature prediction endpoint |
| `/predict/minimal` | POST | Minimal-feature prediction endpoint |

### Full Features Endpoint

**POST** `/predict/full`

Requires all features from `future_unseen_examples.csv`:

```json
{
  "bedrooms": 4,
  "bathrooms": 2.5,
  "sqft_living": 2000,
  "sqft_lot": 8000,
  "floors": 2.0,
  "waterfront": 0,
  "view": 0,
  "condition": 4,
  "grade": 8,
  "sqft_above": 2000,
  "sqft_basement": 0,
  "yr_built": 1990,
  "yr_renovated": 0,
  "zipcode": "98115",
  "lat": 47.6974,
  "long": -122.313,
  "sqft_living15": 1900,
  "sqft_lot15": 8000
}
```

### Minimal Features Endpoint

**POST** `/predict/minimal`

Requires only essential features (bonus requirement):

```json
{
  "bedrooms": 4,
  "bathrooms": 2.5,
  "sqft_living": 2000,
  "sqft_lot": 8000,
  "floors": 2.0,
  "sqft_above": 2000,
  "sqft_basement": 0,
  "zipcode": "98115"
}
```

### Response Format

```json
{
  "prediction": 450000.0,
  "confidence": null,
  "model_version": "1.0.0",
  "features_used": ["bedrooms", "bathrooms", "sqft_living", ...],
  "processing_time_ms": 45.2,
  "metadata": {
    "input_features": {...},
    "demographics_enriched": true,
    "zipcode": "98115",
    "prediction_timestamp": "2024-01-01T12:00:00"
  }
}
```

## Docker Deployment

### Multi-Service with Load Balancing and Scaling

The solution uses Docker Compose with horizontal scaling capabilities:

```bash
# Start with 3 API instances and nginx load balancer
docker-compose up -d

# Check service status
docker-compose ps

# Scale to more instances
docker-compose up -d --scale mle-api=5

# View logs
docker-compose logs nginx
docker-compose logs mle-api
```

### Architecture Components

1. **mle-api service**: FastAPI application with automatic scaling
2. **nginx service**: Load balancer distributing requests across API instances
3. **Automatic scaling**: Docker Compose handles instance management
4. **Health checks**: Built-in health monitoring for all services

### Scaling Configuration

```yaml
# From docker-compose.yml
deploy:
  replicas: 3  # Start with 3 instances
```

Scale dynamically:
```bash
# Scale to 5 instances
docker-compose up -d --scale mle-api=5

# Scale to 2 instances
docker-compose up -d --scale mle-api=2
```

## Model Evaluation

The solution includes comprehensive model evaluation tools:

### Automated Evaluation

```bash
# Run comprehensive evaluation
uv run python tools/evaluate_model.py

# View results
cat evaluation_results/evaluation_report.txt
```

### Evaluation Metrics

- **RMSE**: Root Mean Square Error
- **MAE**: Mean Absolute Error  
- **R²**: Coefficient of determination
- **MAPE**: Mean Absolute Percentage Error
- **Cross-validation**: K-fold cross-validation performance
- **Generalization**: Testing on unseen data

### Performance Analysis

The evaluation script provides:
- **Model performance metrics** on test data
- **Feature importance analysis**
- **Generalization testing** on future examples
- **Performance visualizations** saved to `evaluation_results/`

## Scaling and Deployment Features

### Horizontal Scaling

- **Implemented**: Horizontal scaling through Docker Compose replicas
- **Load Balancing**: nginx automatically distributes requests
- **Health Checks**: Built-in health monitoring
- **Stateless Design**: Easy instance addition/removal

### Zero-Downtime Deployments

- **Model Hot-Swapping**: Update models without stopping service
- **Health Check Integration**: Load balancer automatically routes to healthy instances
- **Graceful Shutdown**: Proper container lifecycle management
- **Rolling Updates**: Deploy new versions without downtime

### Auto-scaling Considerations

For production auto-scaling, the architecture supports:

- **CPU/Memory metrics** for scaling decisions
- **Request queue length** monitoring
- **Response time** thresholds
- **Cost optimization** strategies
- **Integration** with Kubernetes HPA or Docker Swarm

## Testing

### API Testing

```bash
# Test the load-balanced API
uv run python tools/test_api.py
```

The test script:
- Tests both endpoints with real data from `future_unseen_examples.csv`
- Compares predictions between full and minimal features
- Provides comprehensive test results and statistics
- **Meets deliverable requirement #2**: Test script demonstrating service behavior

### Model Testing

```bash
# Run comprehensive model evaluation
uv run python tools/evaluate_model.py
```

**Meets deliverable requirement #3**: Model performance evaluation including:
- Cross-validation analysis
- Feature importance ranking
- Generalization testing on unseen data
- Performance visualization and reporting

## Configuration

### Environment Variables

- `PORT`: API service port (default: 8000)
- `PYTHONPATH`: Python path configuration
- `LOG_LEVEL`: Logging level configuration

### Docker Configuration

- **Memory limits**: Configurable per container
- **CPU limits**: Configurable per container
- **Health checks**: 30-second intervals
- **Restart policy**: Unless stopped
- **Scaling**: Configurable via docker-compose.yml

### Nginx Configuration

- **Load balancing**: Round-robin distribution
- **Rate limiting**: 10 requests/second with burst handling
- **Health checks**: Automatic failover
- **Compression**: Gzip compression enabled
- **Monitoring**: `/nginx_status` endpoint

## Performance Considerations

### Optimization Features

- **Feature preprocessing** with RobustScaler
- **Efficient data loading** and caching
- **Minimal memory footprint** per request
- **Async request handling** with FastAPI
- **Horizontal scaling** for increased throughput

### Monitoring

- **Request processing time** tracking
- **Memory usage** monitoring
- **Error rate** tracking
- **Health status** endpoints
- **Nginx status** monitoring

## Error Handling

The API includes comprehensive error handling:

- **Input validation** using Pydantic models
- **Graceful degradation** for missing demographics
- **Detailed error messages** for debugging
- **HTTP status codes** following REST standards
- **Automatic failover** through load balancer

## Security Considerations

- **Input sanitization** and validation
- **Rate limiting** via nginx configuration
- **Resource limits** per container
- **Health check endpoints** for monitoring
- **Container isolation** through Docker

## Development

### Adding New Features

1. **Extend the API models** in `src/models/requests.py`
2. **Update the ModelService** class in `src/services/model_service.py`
3. **Add routes** in `src/routers/`
4. **Add tests** in `tools/test_api.py`
5. **Update documentation** in this file

### Model Updates

1. **Retrain the model** using `create_model.py`
2. **Replace model files** in the `model/` directory
3. **Restart the service** or use rolling updates
4. **Verify performance** using `tools/evaluate_model.py`

## Deliverable Requirements Compliance

### Requirement 1: RESTful API Endpoint
- **Full-feature endpoint**: Accepts all columns from `future_unseen_examples.csv`
- **Minimal-feature endpoint**: Accepts only required features (bonus requirement)
- **Demographic enrichment**: Automatically adds ZIP code demographics on backend
- **JSON response**: Returns predictions with metadata
- **Scaling solution**: Horizontal scaling with Docker Compose replicas
- **Model updates**: Zero-downtime deployment capability

### Requirement 2: Test Script
- **Comprehensive testing**: Tests both endpoints with real data
- **Real examples**: Uses data from `future_unseen_examples.csv`
- **Service validation**: Demonstrates API functionality

### Requirement 3: Model Evaluation
- **Performance assessment**: Comprehensive evaluation metrics
- **Generalization testing**: Evaluation on unseen data
- **Model fit analysis**: Cross-validation and test set performance

## Production Deployment

### Scaling Commands

```bash
# Start with 3 instances
docker-compose up -d

# Scale to 5 instances
docker-compose up -d --scale mle-api=5

# Scale to 10 instances for high traffic
docker-compose up -d --scale mle-api=10

# Scale down to 2 instances
docker-compose up -d --scale mle-api=2
```

### Monitoring

```bash
# Check service status
docker-compose ps

# View nginx status
curl http://localhost:8000/nginx_status

# Check API health
curl http://localhost:8000/health

# View logs
docker-compose logs -f
```

### Load Testing

```bash
# Test load balancing with multiple requests
for i in {1..20}; do
  curl -s http://localhost:8000/health > /dev/null &
done
wait
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## License

This project is part of the phData Machine Learning Engineer Project Challenge 2.

## Support

For issues and questions:
1. Check the logs: `docker-compose logs`
2. Verify service status: `docker-compose ps`
3. Test API health: `curl http://localhost:8000/health`
4. Check nginx status: `curl http://localhost:8000/nginx_status`

## Success Metrics

This solution successfully addresses all phData MLE project requirements:

- **Production-ready API** with horizontal scaling
- **Zero-downtime deployments** and model updates
- **Comprehensive testing** and evaluation
- **Modern containerization** with Docker Compose
- **Load balancing** with nginx
- **Bonus features** (minimal-feature endpoint)
- **Real-world scalability** considerations
