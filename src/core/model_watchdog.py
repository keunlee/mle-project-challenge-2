import logging
import time
from threading import Thread

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelFileChangeHandler(FileSystemEventHandler):
    def __init__(self, model_service):
        self.model_service = model_service

    # Called when a file is modified
    def on_modified(self, event):
        if event.src_path.endswith("model.pkl"):
            logger.info("Model file changed. Reloading model...")
            self.model_service.reload_model()

# Start the file watcher in a separate thread
def start_file_watcher(model_service, model_dir="model"):
    event_handler = ModelFileChangeHandler(model_service)
    observer = Observer()
    observer.schedule(event_handler, path=model_dir, recursive=False)
    observer.start()
    logger.info("Started file watcher for model changes.")

    def watch():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    Thread(target=watch, daemon=True).start()