import logging
import time

import pandas as pd
from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends

from core.dependencies import get_model_service
from models.requests import PredictionResponse, FullFeatureRequest, MinimalFeatureRequest
from services.model_service import ModelService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/model-info")
async def model_info(request: Request, model_service: ModelService = Depends(get_model_service)):
    """Get model information"""
    return {
        "model_version": model_service.model_version,
        "features_used": model_service.features,
        "feature_count": len(model_service.features),
        "model_type": type(model_service.model).__name__ if model_service.model else None
    }

@router.post("/reload-model")
def reload_model(request: Request, model_service: ModelService = Depends(get_model_service)):
    model_service.reload_model()
    return {"status": "reloaded", "version": model_service.model_version}

@router.post("/predict/full", response_model=PredictionResponse)
async def predict_full_features(request: FullFeatureRequest, fastapi_request: Request, model_service: ModelService = Depends(get_model_service)):
    """Predict house price using all available features"""

    start_time = time.time()

    try:
        # Convert request to dict
        request_dict = request.model_dump()

        # Prepare features
        features_df = model_service.prepare_features(request_dict, minimal=False)

        # Make prediction
        prediction = model_service.predict(features_df)

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000

        # Get demographics for metadata
        demographics = model_service.enrich_with_demographics(request.zipcode)

        return PredictionResponse(
            prediction=prediction,
            confidence=None,  # KNN doesn't provide confidence scores
            model_version=model_service.model_version,
            features_used=model_service.features,
            processing_time_ms=processing_time,
            metadata={
                "input_features": request_dict,
                "demographics_enriched": bool(demographics),
                "zipcode": request.zipcode,
                "prediction_timestamp": pd.Timestamp.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"Error in full feature prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/minimal", response_model=PredictionResponse)
async def predict_minimal_features(request: MinimalFeatureRequest, fastapi_request: Request, model_service: ModelService = Depends(get_model_service)):
    """Predict house price using only essential features (bonus endpoint)"""
    import time
    start_time = time.time()

    try:
        # Convert request to dict
        request_dict = request.model_dump()

        # Prepare features (minimal mode)
        features_df = model_service.prepare_features(request_dict, minimal=True)

        # Make prediction
        prediction = model_service.predict(features_df)

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000

        # Get demographics for metadata
        demographics = model_service.enrich_with_demographics(request.zipcode)

        return PredictionResponse(
            prediction=prediction,
            confidence=None,
            model_version=model_service.model_version,
            features_used=model_service.features,
            processing_time_ms=processing_time,
            metadata={
                "input_features": request_dict,
                "demographics_enriched": bool(demographics),
                "zipcode": request.zipcode,
                "prediction_timestamp": pd.Timestamp.now().isoformat(),
                "note": "Prediction made with minimal features + demographics enrichment"
            }
        )

    except Exception as e:
        logger.error(f"Error in minimal feature prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

