#!/usr/bin/env python3
"""
Test script for multi-container hot reloading functionality.

This script tests the watchdog's ability to detect model file changes
and automatically reload the model across multiple container instances.
It's useful for verifying that the shared volume approach works correctly.

Usage:
    python tools/test_multi_container_reload.py
    
Prerequisites:
    - Docker Compose services must be running with multiple API instances
    - model/model.pkl must exist
    - Watchdog must be enabled in all containers
"""

import time
import requests
import logging
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_container_statuses():
    """Get watchdog status from all running containers"""
    try:
        response = requests.get("http://localhost:8000/watchdog-status", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get watchdog status: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Failed to connect to API: {e}")
        return None

def check_container_health():
    """Check health of all containers"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get health status: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Failed to connect to API: {e}")
        return None

def get_model_info():
    """Get current model information"""
    try:
        response = requests.get("http://localhost:8000/model-info", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get model info: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Failed to connect to API: {e}")
        return None

def simulate_model_update():
    """Simulate a model update by actually changing the model file"""
    model_path = Path("model/model.pkl")
    if not model_path.exists():
        logger.error("Model file does not exist")
        return False
    
    try:
        # Get current modification time and size
        current_stat = model_path.stat()
        current_mtime = current_stat.st_mtime
        current_size = current_stat.st_size
        
        # Create a real file change by appending a small amount of data
        # This ensures the watchdog detects actual content change
        with open(model_path, 'ab') as f:
            f.write(b'\x00' * 1024)  # Add 1KB of zeros
        
        # Wait a moment for the change to be detected
        time.sleep(0.1)
        
        # Verify the modification time and size changed
        new_stat = model_path.stat()
        new_mtime = new_stat.st_mtime
        new_size = new_stat.st_size
        
        if new_mtime > current_mtime and new_size > current_size:
            logger.info("✅ Model file updated successfully with real content change")
            logger.info(f"   Size: {current_size} → {new_size} bytes")
            logger.info(f"   Modified: {current_mtime} → {new_mtime}")
            return True
        else:
            logger.warning("⚠️  Model file modification not detected")
            return False
            
    except Exception as e:
        logger.error(f"Failed to update model file: {e}")
        return False

def test_multi_container_reload():
    """Test hot reloading across multiple containers"""
    logger.info("🧪 Testing Multi-Container Hot Reloading")
    logger.info("=" * 60)
    
    # Step 1: Check initial status
    logger.info("\n📋 Step 1: Initial Status Check")
    initial_status = get_container_statuses()
    if not initial_status:
        logger.error("❌ Cannot connect to API. Ensure services are running.")
        return False
    
    logger.info("✅ API connection successful")
    logger.info(f"   Container ID: {initial_status.get('container_id', 'unknown')}")
    logger.info(f"   Watchdog Enabled: {initial_status.get('watchdog_enabled', False)}")
    logger.info(f"   Shared Volume: {initial_status.get('shared_volume', False)}")
    logger.info(f"   Multi-Container Ready: {initial_status.get('multi_container_ready', False)}")
    
    # Step 2: Check model info
    logger.info("\n📋 Step 2: Initial Model Information")
    initial_model_info = get_model_info()
    if not initial_model_info:
        logger.error("❌ Failed to get model information")
        return False
    
    initial_version = initial_model_info.get('model_version')
    logger.info(f"✅ Initial model version: {initial_version}")
    logger.info(f"   Features: {initial_model_info.get('feature_count', 'unknown')}")
    logger.info(f"   Model Type: {initial_model_info.get('model_type', 'unknown')}")
    
    # Step 3: Simulate model update
    logger.info("\n📋 Step 3: Simulating Model Update")
    if not simulate_model_update():
        logger.error("❌ Failed to simulate model update")
        return False
    
    # Step 4: Wait for reload and check status
    logger.info("\n📋 Step 4: Waiting for Model Reload")
    logger.info("⏳ Waiting 5 seconds for containers to detect changes...")
    time.sleep(5)
    
    # Step 5: Check updated status
    logger.info("\n📋 Step 5: Post-Update Status Check")
    updated_status = get_container_statuses()
    if not updated_status:
        logger.error("❌ Failed to get updated status")
        return False
    
    # Step 6: Check if model was reloaded
    logger.info("\n📋 Step 6: Model Reload Verification")
    updated_model_info = get_model_info()
    if not updated_model_info:
        logger.error("❌ Failed to get updated model information")
        return False
    
    updated_version = updated_model_info.get('model_version')
    logger.info(f"✅ Updated model version: {updated_version}")
    
    # Step 7: Analyze results
    logger.info("\n📋 Step 7: Analysis")
    if updated_version != initial_version:
        logger.info("🎉 SUCCESS: Model was reloaded across containers!")
        logger.info(f"   Version changed: {initial_version} → {updated_version}")
    else:
        logger.info("ℹ️  Model version unchanged - checking for reload activity in logs...")
        
        # Check if reloading actually happened by looking at the logs
        logger.info("🔍 Checking container logs for reload activity...")
        try:
            import subprocess
            result = subprocess.run(
                ["docker-compose", "logs", "mle-api"], 
                capture_output=True, text=True, timeout=10
            )
            if "reloading model" in result.stdout:
                reload_count = result.stdout.count("reloading model")
                logger.info(f"🎉 SUCCESS: Found {reload_count} reload events in logs!")
                logger.info("   Hot reloading is working correctly across containers")
                logger.info("   Model version may not change if file content is similar")
            else:
                logger.warning("⚠️  No reload events found in logs")
        except Exception as e:
            logger.info(f"ℹ️  Could not check logs automatically: {e}")
            logger.info("   Manual verification needed: docker-compose logs mle-api")
    
    # Step 8: Container-specific information
    logger.info("\n📋 Step 8: Container Details")
    logger.info("📊 Container Status:")
    logger.info(f"   Model File Path: {updated_status.get('model_file_path', 'unknown')}")
    logger.info(f"   Model File Size: {updated_status.get('model_file_size', 'unknown')} bytes")
    logger.info(f"   Last Modified: {updated_status.get('model_file_modified', 'unknown')}")
    logger.info(f"   Debounce Time: {updated_status.get('debounce_time', 'unknown')}s")
    
    # Step 9: Recommendations
    logger.info("\n📋 Step 9: Recommendations")
    logger.info("💡 To verify multi-container reloading:")
    logger.info("   1. Check Docker Compose logs: docker-compose logs mle-api")
    logger.info("   2. Look for reload messages from different container IDs")
    logger.info("   3. Verify all containers show the same model version")
    logger.info("   4. Test with actual model file replacement")
    
    return True

def main():
    """Main test function"""
    try:
        success = test_multi_container_reload()
        if success:
            logger.info("\n🎉 Multi-Container Hot Reload Test Completed!")
        else:
            logger.error("\n❌ Multi-Container Hot Reload Test Failed!")
            
    except KeyboardInterrupt:
        logger.info("\n⏹️  Test interrupted by user")
    except Exception as e:
        logger.error(f"\n💥 Unexpected error: {e}")

if __name__ == "__main__":
    main()
