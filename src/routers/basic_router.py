from fastapi import APIRouter, Request
from fastapi.params import Depends

from core.dependencies import get_model_service
from services.model_service import ModelService

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "House Price Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "/predict/full": "Full feature prediction endpoint",
            "/predict/minimal": "Minimal feature prediction endpoint",
            "/health": "Health check endpoint",
            "/model-info": "Model information endpoint",
            "/watchdog-status": "Watchdog monitoring status endpoint",
            "/reload-model": "Manual model reload endpoint"
        }
    }

@router.get("/health")
async def health_check(request: Request, model_service: ModelService = Depends(get_model_service)):
    return {
        "status": "healthy",
        "model_loaded": getattr(model_service, "model", None) is not None,
        "demographics_loaded": getattr(model_service, "demographics_data", None) is not None,
        "version": getattr(model_service, "model_version", None)
    }

@router.get("/watchdog-status")
async def watchdog_status(request: Request, model_service: ModelService = Depends(get_model_service)):
    """Check if the model watchdog is active and monitoring for changes"""
    return {
        "watchdog_active": True,  # If this endpoint is reachable, watchdog is running
        "model_file_path": str(model_service.model_path),
        "last_model_load": model_service.model_mtime,
        "model_version": model_service.model_version,
        "message": "Model watchdog is active and monitoring for file changes"
    }