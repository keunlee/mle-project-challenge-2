import logging
import os
import time
from pathlib import Path
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logger = logging.getLogger(__name__)


class ModelFileChangeHandler(FileSystemEventHandler):
    """
    File system event handler for monitoring model file changes.

    This handler automatically reloads the model when the model.pkl file
    is modified, enabling hot-reloading during development and deployment.

    Enhanced for multi-container environments with shared volumes.
    """

    def __init__(self, model_service):
        self.model_service = model_service
        self.last_modified = 0
        self.debounce_time = float(os.getenv('MODEL_RELOAD_DEBOUNCE', '1.0'))
        self.container_id = os.getenv('HOSTNAME', 'unknown')
        logger.info(f"Watchdog initialized for container {self.container_id} with {self.debounce_time}s debounce")

    def on_modified(self, event):
        """
        Handle file modification events.

        Args:
            event: FileSystemEvent containing information about the change
        """
        if not event.is_directory and event.src_path.endswith("model.pkl"):
            current_time = time.time()

            # Debounce to prevent multiple rapid reloads
            if current_time - self.last_modified > self.debounce_time:
                logger.info(f"Model file changed: {event.src_path}")
                logger.info(f"Container {self.container_id} reloading model...")

                try:
                    # Get current model version before reload
                    old_version = getattr(self.model_service, 'model_version', 'unknown')

                    # Reload the model
                    self.model_service.reload_model()

                    # Get new model version
                    new_version = getattr(self.model_service, 'model_version', 'unknown')

                    logger.info(f"Container {self.container_id} model reloaded successfully")
                    logger.info(f"Model version: {old_version} → {new_version}")

                    # Log model file details
                    model_path = Path(event.src_path)
                    if model_path.exists():
                        stat = model_path.stat()
                        logger.info(f"Model file size: {stat.st_size} bytes, modified: {stat.st_mtime}")

                except Exception as e:
                    logger.error(f"Container {self.container_id} failed to reload model: {e}")

                self.last_modified = current_time
            else:
                logger.debug(f"Container {self.container_id}: Model file change detected but debounced")

    def on_created(self, event):
        """Handle file creation events (e.g., new model file)"""
        if not event.is_directory and event.src_path.endswith("model.pkl"):
            logger.info(f"Container {self.container_id}: New model file detected: {event.src_path}")
            # Trigger reload for new files
            self.on_modified(event)

    def on_moved(self, event):
        """Handle file move events (e.g., model replacement)"""
        if not event.is_directory and event.dest_path.endswith("model.pkl"):
            logger.info(f"Container {self.container_id}: Model file moved to: {event.dest_path}")
            # Trigger reload for moved files
            self.on_modified(event)


def start_file_watcher(model_service, model_dir="model"):
    """
    Start the file watcher to monitor model file changes.

    Args:
        model_service: The ModelService instance to reload when files change
        model_dir: Directory to monitor for changes (default: "model")

    The watchdog runs in a background thread and automatically reloads
    the model when model.pkl is modified, enabling zero-downtime updates
    across multiple containers with shared volumes.
    """
    try:
        # Check if watchdog is enabled via environment variable
        if not os.getenv('MODEL_WATCHDOG_ENABLED', 'true').lower() in ('true', '1', 'yes'):
            logger.info("Model watchdog disabled via environment variable")
            return False

        # Ensure the model directory exists
        model_path = Path(model_dir)
        if not model_path.exists():
            logger.error(f"Model directory {model_dir} does not exist")
            return False

        # Check if model.pkl exists
        model_file = model_path / "model.pkl"
        if not model_file.exists():
            logger.warning(f"Model file {model_file} does not exist yet")
            logger.info("Watchdog will monitor for model file creation")

        # Create event handler and observer
        event_handler = ModelFileChangeHandler(model_service)
        observer = Observer()

        # Schedule the event handler to watch the model directory
        observer.schedule(event_handler, path=str(model_path), recursive=False)

        # Start the observer
        observer.start()
        container_id = os.getenv('HOSTNAME', 'unknown')
        logger.info(f"Container {container_id}: Started file watcher for model changes in {model_dir}/")

        # Start monitoring in background thread
        def watch():
            try:
                while observer.is_alive():
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info(f"Container {container_id}: Stopping file watcher...")
                observer.stop()
            finally:
                observer.join()
                logger.info(f"Container {container_id}: File watcher stopped")

        # Start monitoring thread as daemon (will stop when main process stops)
        watch_thread = Thread(target=watch, daemon=True, name=f"ModelWatchdog-{container_id}")
        watch_thread.start()

        return True

    except Exception as e:
        logger.error(f"Failed to start file watcher: {e}")
        return False

def get_watchdog_status():
    """
    Get the current status of the watchdog system.

    Returns:
        dict: Status information about the watchdog
    """
    container_id = os.getenv('HOSTNAME', 'unknown')
    model_dir = os.getenv('MODEL_DIR', 'model')
    watchdog_enabled = os.getenv('MODEL_WATCHDOG_ENABLED', 'true').lower() in ('true', '1', 'yes')

    status = {
        "watchdog_enabled": watchdog_enabled,
        "container_id": container_id,
        "model_directory": model_dir,
        "debounce_time": float(os.getenv('MODEL_RELOAD_DEBOUNCE', '1.0')),
        "shared_volume": True,  # Indicates this is designed for shared volumes
        "multi_container_ready": True
    }

    # Check if model file exists and get its details
    model_path = Path(model_dir) / "model.pkl"
    if model_path.exists():
        stat = model_path.stat()
        status.update({
            "model_file_exists": True,
            "model_file_size": stat.st_size,
            "model_file_modified": stat.st_mtime,
            "model_file_path": str(model_path)
        })
    else:
        status.update({
            "model_file_exists": False,
            "model_file_path": str(model_path)
        })

    return status
