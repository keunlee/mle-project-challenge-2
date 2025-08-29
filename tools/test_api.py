#!/usr/bin/env python3
"""
Test script for the House Price Prediction API.

This script provides comprehensive testing of the deployed API by:
1. Checking API health and model information
2. Testing both prediction endpoints (full and minimal features)
3. Submitting real examples from future_unseen_examples.csv
4. Comparing predictions between endpoints
5. Providing detailed test results and statistics

The script serves as both a testing tool and a demonstration of how
to interact with the API programmatically. It validates that the
deployed model can handle real-world data and produce reasonable
predictions across different feature sets.

Usage:
    python tools/test_api.py

Prerequisites:
    - API must be running on http://localhost:8000
    - future_unseen_examples.csv must be available in data/ directory
"""

import logging
import time
from typing import Dict

import pandas as pd
import requests

# Configure structured logging for better debugging and monitoring
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# API endpoint configuration
# These URLs point to the nginx load balancer which distributes requests
# across multiple API instances for scalability
BASE_URL = "http://localhost:8000"  # Base URL for the API (via nginx)
FULL_ENDPOINT = f"{BASE_URL}/predict/full"  # Full-feature prediction endpoint
MINIMAL_ENDPOINT = f"{BASE_URL}/predict/minimal"  # Minimal-feature prediction endpoint
HEALTH_ENDPOINT = f"{BASE_URL}/health"  # Health check endpoint
MODEL_INFO_ENDPOINT = f"{BASE_URL}/model-info"  # Model information endpoint


def check_api_health() -> bool:
    """
    Check if the API is running and healthy.

    This function performs a health check by calling the /health endpoint
    to verify that the API service is operational and responding correctly.

    Returns:
        bool: True if API is healthy, False otherwise

    The health check validates:
    - API service is running and accessible
    - Health endpoint returns 200 status
    - Response contains expected 'status': 'healthy' field
    """
    try:
        # Make GET request to health endpoint with 10 second timeout
        response = requests.get(HEALTH_ENDPOINT, timeout=10)

        if response.status_code == 200:
            # Parse JSON response to check health status
            health_data = response.json()
            logger.info(f"API Health Check: {health_data}")

            # Return True only if status field indicates 'healthy'
            return health_data.get("status") == "healthy"
        else:
            # Log error for non-200 status codes
            logger.error(
                f"Health check failed with status code: {response.status_code}"
            )
            return False

    except requests.exceptions.RequestException as e:
        # Handle network errors, timeouts, and connection failures
        logger.error(f"Failed to connect to API: {e}")
        return False


def get_model_info() -> Dict:
    """
    Retrieve information about the currently loaded ML model.

    This function calls the /model-info endpoint to get metadata about
    the deployed model, including feature names, model type, and version.

    Returns:
        Dict: Model information dictionary if successful, empty dict if failed

    The model info typically includes:
    - Model type and algorithm details
    - Feature names and descriptions
    - Model version and training date
    - Performance metrics and configuration
    """
    try:
        # Make GET request to model info endpoint with 10 second timeout
        response = requests.get(MODEL_INFO_ENDPOINT, timeout=10)

        if response.status_code == 200:
            # Parse JSON response containing model metadata
            model_info = response.json()
            logger.info(f"Model Info: {model_info}")
            return model_info
        else:
            # Log error for non-200 status codes
            logger.error(f"Failed to get model info: {response.status_code}")
            return {}

    except requests.exceptions.RequestException as e:
        # Handle network errors, timeouts, and connection failures
        logger.error(f"Failed to get model info: {e}")
        return {}


def load_test_data() -> pd.DataFrame:
    """
    Load test data from the future_unseen_examples.csv file.

    This function reads the CSV file containing house examples that were
    not used during model training, providing realistic test cases for
    API validation.

    Returns:
        pd.DataFrame: DataFrame containing test examples with house features

    The test data includes:
    - Basic structural features (bedrooms, bathrooms, square footage)
    - Location information (ZIP codes)
    - Features that match the API endpoint requirements

    Raises:
        Exception: If file cannot be loaded or parsed
    """
    try:
        # Define path to test data file
        data_path = "data/future_unseen_examples.csv"

        # Load CSV data into pandas DataFrame
        df = pd.read_csv(data_path)

        # Log successful data loading with count
        logger.info(f"Loaded {len(df)} test examples from {data_path}")
        return df

    except Exception as e:
        # Log error and re-raise for caller to handle
        logger.error(f"Failed to load test data: {e}")
        raise


def test_full_features_endpoint(example_data: Dict) -> Dict:
    """
    Test the full-features prediction endpoint with comprehensive house data.

    This function sends a POST request to the /predict/full endpoint with
    all available house features to test the complete prediction capability.

    Args:
        example_data (Dict): Dictionary containing all house features including
                           bedrooms, bathrooms, square footage, location, etc.

    Returns:
        Dict: Prediction result if successful, empty dict if failed

    The full features endpoint requires:
    - All structural features (bedrooms, bathrooms, square footage)
    - Location features (ZIP code, latitude, longitude)
    - Additional features (waterfront, view, condition, grade, etc.)
    - Historical data (year built, renovation year)
    """
    try:
        # Log which example we're testing (identified by ZIP code)
        logger.info(
            f"Testing full features endpoint with example: {example_data['zipcode']}"
        )

        # Send POST request to full features endpoint
        # Use 30 second timeout for potentially complex predictions
        response = requests.post(
            FULL_ENDPOINT,
            json=example_data,  # Send all features as JSON payload
            timeout=30,
        )

        if response.status_code == 200:
            # Parse successful prediction response
            result = response.json()
            logger.info(
                f"✅ Full features prediction successful: ${result['prediction']:,.2f}"
            )
            return result
        else:
            # Log error details for failed requests
            logger.error(
                f"❌ Full features prediction failed: {response.status_code} - {response.text}"
            )
            return {}

    except requests.exceptions.RequestException as e:
        # Handle network errors, timeouts, and connection failures
        logger.error(f"❌ Request failed: {e}")
        return {}


def test_minimal_features_endpoint(example_data: Dict) -> Dict:
    """
    Test the minimal-features prediction endpoint with essential house data only.

    This function extracts only the core features required by the minimal endpoint
    and sends a POST request to test the simplified prediction capability.

    Args:
        example_data (Dict): Dictionary containing all house features (only some will be used)

    Returns:
        Dict: Prediction result if successful, empty dict if failed

    The minimal features endpoint requires only:
    - Essential structural features (bedrooms, bathrooms, square footage)
    - Basic location (ZIP code)
    - Core building characteristics (floors, above/basement square footage)

    This tests the bonus requirement of making predictions with limited information.
    """
    try:
        # Extract only the minimal features required by the minimal endpoint
        # This simulates real-world scenarios where limited data is available
        minimal_features = {
            "bedrooms": example_data["bedrooms"],
            "bathrooms": example_data["bathrooms"],
            "sqft_living": example_data["sqft_living"],
            "sqft_lot": example_data["sqft_lot"],
            "floors": example_data["floors"],
            "sqft_above": example_data["sqft_above"],
            "sqft_basement": example_data["sqft_basement"],
            "zipcode": example_data["zipcode"],
        }

        # Log which example we're testing (identified by ZIP code)
        logger.info(
            f"Testing minimal features endpoint with example: {str(minimal_features['zipcode'])}"
        )

        # Send POST request to minimal features endpoint
        # Use 30 second timeout for predictions
        response = requests.post(
            MINIMAL_ENDPOINT,
            json=minimal_features,  # Send only minimal features as JSON payload
            timeout=30,
        )

        if response.status_code == 200:
            # Parse successful prediction response
            result = response.json()
            logger.info(
                f"✅ Minimal features prediction successful: ${result['prediction']:,.2f}"
            )
            return result
        else:
            # Log error details for failed requests
            logger.error(
                f"❌ Minimal features prediction failed: {response.status_code} - {response.text}"
            )
            return {}

    except requests.exceptions.RequestException as e:
        # Handle network errors, timeouts, and connection failures
        logger.error(f"❌ Request failed: {e}")
        return {}


def compare_predictions(full_result: Dict, minimal_result: Dict) -> None:
    """
    Compare predictions from both endpoints to assess prediction consistency.

    This function analyzes how similar the predictions are when using
    full features vs. minimal features, providing insights into the
    model's robustness and feature importance.

    Args:
        full_result (Dict): Prediction result from full-features endpoint
        minimal_result (Dict): Prediction result from minimal-features endpoint

    The comparison provides:
    - Absolute dollar difference between predictions
    - Percentage difference for relative assessment
    - Qualitative assessment of prediction similarity
    - Insights into whether additional features significantly improve accuracy
    """
    if full_result and minimal_result:
        # Extract prediction values from both results
        full_pred = full_result["prediction"]
        minimal_pred = minimal_result["prediction"]

        # Calculate absolute and percentage differences
        difference = abs(full_pred - minimal_pred)
        percentage_diff = (difference / full_pred) * 100

        # Log detailed comparison results
        logger.info("📊 Prediction Comparison:")
        logger.info(f"   Full features:     ${full_pred:,.2f}")
        logger.info(f"   Minimal features:  ${minimal_pred:,.2f}")
        logger.info(
            f"   Difference:        ${difference:,.2f} ({percentage_diff:.2f}%)"
        )

        # Provide qualitative assessment based on percentage difference
        if percentage_diff < 5:
            logger.info("   ✅ Predictions are very similar (< 5% difference)")
        elif percentage_diff < 15:
            logger.info("   ⚠️  Predictions are reasonably similar (< 15% difference)")
        else:
            logger.info("   ❌ Predictions differ significantly (> 15% difference)")


def run_comprehensive_test(num_examples: int = 5) -> None:
    """
    Run a comprehensive test of the API with multiple examples.

    This function orchestrates the complete testing process by:
    1. Validating API health and model availability
    2. Loading test data from CSV file
    3. Testing both endpoints with multiple examples
    4. Comparing predictions for consistency
    5. Providing detailed test summary and success rates

    Args:
        num_examples (int): Number of test examples to run (default: 5)

    The comprehensive test validates:
    - API service availability and health
    - Model information retrieval
    - Both prediction endpoints functionality
    - Prediction consistency between feature sets
    - Overall system reliability and performance
    """
    logger.info("🚀 Starting comprehensive API test")

    # Step 1: Validate API health before proceeding
    if not check_api_health():
        logger.error("❌ API is not healthy. Please start the service first.")
        return

    # Step 2: Verify model information is accessible
    model_info = get_model_info()
    if not model_info:
        logger.error("❌ Failed to get model information")
        return

    # Step 3: Load test data for validation
    try:
        test_df = load_test_data()
    except Exception as e:
        logger.error(f"❌ Failed to load test data: {e}")
        return

    # Step 4: Execute tests with multiple examples
    successful_tests = 0
    total_tests = min(num_examples, len(test_df))  # Don't exceed available examples

    logger.info(f"📋 Testing with {total_tests} examples")

    # Test each example individually
    for i in range(total_tests):
        # Convert DataFrame row to dictionary and ensure ZIP code format
        example = test_df.iloc[i].to_dict()
        example["zipcode"] = str(int(example["zipcode"])).zfill(
            5
        )  # Ensures 5-digit string

        logger.info(f"\n--- Test {i + 1}/{total_tests} ---")

        # Test full features endpoint with complete data
        full_result = test_full_features_endpoint(example)

        # Test minimal features endpoint with essential data only
        minimal_result = test_minimal_features_endpoint(example)

        # Compare predictions and track success
        if full_result and minimal_result:
            compare_predictions(full_result, minimal_result)
            successful_tests += 1
        else:
            logger.error(f"❌ Test {i + 1} failed")

        # Small delay between tests to avoid overwhelming the API
        time.sleep(0.5)

    # Step 5: Provide comprehensive test summary
    logger.info("\n📊 Test Summary:")
    logger.info(f"   Total tests: {total_tests}")
    logger.info(f"   Successful: {successful_tests}")
    logger.info(f"   Failed: {total_tests - successful_tests}")
    logger.info(f"   Success rate: {(successful_tests / total_tests) * 100:.1f}%")

    # Final assessment
    if successful_tests == total_tests:
        logger.info("🎉 All tests passed successfully!")
    else:
        logger.warning("⚠️  Some tests failed. Check the logs above for details.")


def run_single_test() -> None:
    """
    Run a single test with a specific example for quick validation.

    This function provides a lightweight testing option for rapid
    API validation without running the full comprehensive test suite.

    The single test:
    - Uses the first example from the test dataset
    - Tests both prediction endpoints
    - Compares predictions for consistency
    - Provides immediate feedback on API functionality

    Useful for:
    - Quick API health checks
    - Development and debugging
    - Single example validation
    """
    logger.info("🧪 Running single test")

    # Load test data and use the first example
    test_df = load_test_data()
    example = test_df.iloc[0].to_dict()

    # Ensure ZIP code is properly formatted as 5-digit string
    example["zipcode"] = str(int(example["zipcode"])).zfill(5)

    # Log test details for transparency
    logger.info(f"Testing with example: ZIP {example['zipcode']}")
    logger.info(
        f"Features: {example['bedrooms']} bed, {example['bathrooms']} bath, {example['sqft_living']} sqft"
    )

    # Test both endpoints with the same example
    full_result = test_full_features_endpoint(example)
    minimal_result = test_minimal_features_endpoint(example)

    # Compare predictions to assess consistency
    compare_predictions(full_result, minimal_result)


def main():
    """
    Main entry point for the API test suite.

    This function orchestrates the complete testing workflow:
    1. Displays test suite header and information
    2. Performs initial API health validation
    3. Executes comprehensive testing with multiple examples
    4. Handles user interruptions and errors gracefully

    The main function serves as the primary interface for running
    the test suite and provides clear feedback on test execution.

    Usage:
        python tools/test_api.py

    Prerequisites:
        - API must be running on http://localhost:8000
        - Test data must be available in data/future_unseen_examples.csv
    """
    logger.info("🏠 House Price Prediction API Test Suite")
    logger.info("=" * 50)

    full_url = "http://localhost:8000/predict/full"
    minimal_url = "http://localhost:8000/predict/minimal"

    # Example payloads for manual testing (these appear to be unused in current flow)
    # These could be used for quick manual endpoint validation
    full_payload = {
        "bedrooms": 3,
        "bathrooms": 2.0,
        "sqft_living": 1560,
        "sqft_lot": 4080,
        "floors": 2.0,
        "waterfront": 0,
        "view": 0,
        "condition": 3,
        "grade": 7,
        "sqft_above": 1560,
        "sqft_basement": 0,
        "yr_built": 1923,
        "yr_renovated": 1982,
        "zipcode": "98115",
        "lat": 47.6892,
        "long": -122.319,
        "sqft_living15": 1900,
        "sqft_lot15": 4080,
    }
    minimal_payload = {
        "bedrooms": 3,
        "bathrooms": 2.0,
        "sqft_living": 1560,
        "sqft_lot": 4080,
        "floors": 2.0,
        "sqft_above": 1560,
        "sqft_basement": 0,
        "zipcode": "98115",
    }

    full_pred = requests.post(full_url, json=full_payload).json()
    minimal_pred = requests.post(minimal_url, json=minimal_payload).json()

    try:
        # Step 1: Validate API is running and healthy
        if not check_api_health():
            logger.error("❌ API is not running. Please start the service with:")
            logger.error("   python api_service.py")
            return

        # Step 2: Execute comprehensive test suite
        run_comprehensive_test(num_examples=5)

    except KeyboardInterrupt:
        # Handle user interruption gracefully
        logger.info("\n⏹️  Test interrupted by user")
    except Exception as e:
        # Log and re-raise unexpected errors for debugging
        logger.error(f"❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    """
    Script execution guard - only run main() if this file is executed directly.
    This allows the script to be imported as a module without automatically
    running the test suite.
    """
    main()
