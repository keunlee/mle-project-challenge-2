import logging

from fastapi import FastAPI

from core.logging_config import setup_logging
from core.model_watchdog import start_file_watcher
from routers import basic_router, model_router
from services.model_service import ModelService

setup_logging()
logger = logging.getLogger(__name__)

# Create a global model service instance
model_service = ModelService()

app = FastAPI(
    title="MLE Project",
    description="MLE Project",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(basic_router.router)
app.include_router(model_router.router)

# Store model service in app state for access by routers
app.state.model_service = model_service


def start_watchdog():
    """Start the model file watchdog in a background thread"""
    try:
        logger.info("Starting model file watchdog...")
        start_file_watcher(model_service, model_dir="model")
        logger.info("Model file watchdog started successfully")
    except Exception as e:
        logger.error(f"Failed to start model file watchdog: {e}")


@app.on_event("startup")
async def startup_event():
    """Start the model file watchdog when the application starts"""
    logger.info("Starting model file watchdog...")
    start_watchdog()


def main():
    logger.info("App starting...")
    logger.debug("Debugging details here")


if __name__ == "__main__":
    main()
