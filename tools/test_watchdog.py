#!/usr/bin/env python3
"""
Test script for the Model Watchdog functionality.

This script tests the watchdog's ability to detect model file changes
and automatically reload the model. It's useful for verifying that
the watchdog is properly integrated and functioning.

Usage:
    python tools/test_watchdog.py

Prerequisites:
    - API must be running with watchdog enabled
    - model/model.pkl must exist
"""

import time
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_watchdog_status():
    """Test the watchdog status endpoint"""
    try:
        response = requests.get("http://localhost:8000/watchdog-status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            logger.info("✅ Watchdog Status:")
            logger.info(f"   Active: {status.get('watchdog_active')}")
            logger.info(f"   Model Path: {status.get('model_file_path')}")
            logger.info(f"   Model Version: {status.get('model_version')}")
            logger.info(f"   Message: {status.get('message')}")
            return True
        else:
            logger.error(f"❌ Watchdog status check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to check watchdog status: {e}")
        return False


def test_model_info():
    """Test the model info endpoint to get current model version"""
    try:
        response = requests.get("http://localhost:8000/model-info", timeout=10)
        if response.status_code == 200:
            info = response.json()
            logger.info("✅ Model Info:")
            logger.info(f"   Version: {info.get('model_version')}")
            logger.info(f"   Features: {info.get('feature_count')}")
            logger.info(f"   Model Type: {info.get('model_type')}")
            return info.get("model_version")
        else:
            logger.error(f"❌ Model info check failed: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"❌ Failed to get model info: {e}")
        return None


def test_model_reload():
    """Test the manual model reload endpoint"""
    try:
        response = requests.post("http://localhost:8000/reload-model", timeout=10)
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ Manual Model Reload:")
            logger.info(f"   Status: {result.get('status')}")
            logger.info(f"   Version: {result.get('version')}")
            return True
        else:
            logger.error(f"❌ Manual reload failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to manually reload model: {e}")
        return False


def main():
    """Main test function"""
    logger.info("🧪 Testing Model Watchdog Functionality")
    logger.info("=" * 50)

    # Test 1: Check if watchdog is active
    logger.info("\n📋 Test 1: Watchdog Status Check")
    if not test_watchdog_status():
        logger.error("❌ Watchdog is not active. Please ensure the API is running.")
        return

    # Test 2: Get initial model version
    logger.info("\n📋 Test 2: Initial Model Version")
    initial_version = test_model_info()
    if not initial_version:
        logger.error("❌ Failed to get initial model version")
        return

    # Test 3: Test manual reload
    logger.info("\n📋 Test 3: Manual Model Reload")
    if not test_model_reload():
        logger.error("❌ Manual reload test failed")
        return

    # Test 4: Check if version changed after reload
    logger.info("\n📋 Test 4: Version Change After Reload")
    time.sleep(1)  # Give the reload time to complete
    new_version = test_model_info()

    if new_version and new_version != initial_version:
        logger.info("✅ Model version changed after reload (as expected)")
        logger.info(f"   Before: {initial_version}")
        logger.info(f"   After:  {new_version}")
    else:
        logger.info(
            "ℹ️  Model version unchanged (this is normal if no actual file changes)"
        )

    logger.info("\n🎉 Watchdog Test Complete!")
    logger.info("\n💡 To test automatic reloading:")
    logger.info("   1. Keep this script running")
    logger.info("   2. Modify or replace model/model.pkl in another terminal")
    logger.info("   3. Watch for automatic reload messages in the API logs")


if __name__ == "__main__":
    main()
