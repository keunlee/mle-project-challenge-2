import logging
import time
from pathlib import Path
from threading import Thread

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Configure logging
logger = logging.getLogger(__name__)


class ModelFileChangeHandler(FileSystemEventHandler):
    """
    File system event handler for monitoring model file changes.

    This handler automatically reloads the model when the model.pkl file
    is modified, enabling hot-reloading during development and deployment.
    """

    def __init__(self, model_service):
        self.model_service = model_service
        self.last_modified = 0
        self.debounce_time = 1.0  # Prevent multiple reloads within 1 second

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
                logger.info("Reloading model...")

                try:
                    self.model_service.reload_model()
                    logger.info("Model reloaded successfully")
                except Exception as e:
                    logger.error(f"Failed to reload model: {e}")

                self.last_modified = current_time
            else:
                logger.debug("Model file change detected but debounced")


def start_file_watcher(model_service, model_dir="model"):
    """
    Start the file watcher to monitor model file changes.

    Args:
        model_service: The ModelService instance to reload when files change
        model_dir: Directory to monitor for changes (default: "model")

    The watchdog runs in a background thread and automatically reloads
    the model when model.pkl is modified, enabling zero-downtime updates.
    """
    try:
        # Ensure the model directory exists
        model_path = Path(model_dir)
        if not model_path.exists():
            logger.error(f"Model directory {model_dir} does not exist")
            return False

        # Create event handler and observer
        event_handler = ModelFileChangeHandler(model_service)
        observer = Observer()

        # Schedule the event handler to watch the model directory
        observer.schedule(event_handler, path=str(model_path), recursive=False)

        # Start the observer
        observer.start()
        logger.info(f"Started file watcher for model changes in {model_dir}/")

        # Start monitoring in background thread
        def watch():
            try:
                while observer.is_alive():
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopping file watcher...")
                observer.stop()
            finally:
                observer.join()
                logger.info("File watcher stopped")

        # Start monitoring thread as daemon (will stop when main process stops)
        watch_thread = Thread(target=watch, daemon=True, name="ModelWatchdog")
        watch_thread.start()

        return True

    except Exception as e:
        logger.error(f"Failed to start file watcher: {e}")
        return False
