import logging

from fastapi import FastAPI

from core.logging_config import setup_logging
from routers import basic_router, model_router

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MLE Project",
    description="MLE Project",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(basic_router.router)
app.include_router(model_router.router)

def main():
    logger.info("App starting...")
    logger.debug("Debugging details here")


if __name__ == "__main__":
    main()
