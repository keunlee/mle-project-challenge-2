from fastapi import Request
from services.model_service import ModelService


def get_model_service(request: Request) -> ModelService:
    """
    Get the model service instance from the FastAPI app state.

    This ensures we're using the same model service instance that's being
    monitored by the watchdog for automatic model reloading.
    """
    return request.app.state.model_service
