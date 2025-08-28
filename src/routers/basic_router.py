from fastapi import APIRouter
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
            "/model-info": "Model information endpoint"
        }
    }

@router.get("/health")
async def health_check(model_service: ModelService = Depends(get_model_service)):
    return {
        "status": "healthy",
        "model_loaded": getattr(model_service, "model", None) is not None,
        "demographics_loaded": getattr(model_service, "demographics_data", None) is not None,
        "version": getattr(model_service, "model_version", None)
    }