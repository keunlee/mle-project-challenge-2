from typing import Optional, Dict, List

from pydantic import BaseModel, Field


# Data models for API requests
class FullFeatureRequest(BaseModel):
    bedrooms: int = Field(..., ge=0, description="Number of bedrooms")
    bathrooms: float = Field(..., ge=0, description="Number of bathrooms")
    sqft_living: int = Field(..., ge=0, description="Square footage of living space")
    sqft_lot: int = Field(..., ge=0, description="Square footage of lot")
    floors: float = Field(..., ge=0, description="Number of floors")
    waterfront: int = Field(..., ge=0, le=1, description="Waterfront property (0 or 1)")
    view: int = Field(..., ge=0, le=4, description="View rating (0-4)")
    condition: int = Field(..., ge=1, le=5, description="Condition rating (1-5)")
    grade: int = Field(..., ge=1, le=13, description="Grade rating (1-13)")
    sqft_above: int = Field(..., ge=0, description="Square footage above ground")
    sqft_basement: int = Field(..., ge=0, description="Square footage of basement")
    yr_built: int = Field(..., ge=1800, le=2024, description="Year built")
    yr_renovated: int = Field(..., ge=0, le=2024, description="Year renovated (0 if never)")
    zipcode: str = Field(..., min_length=5, max_length=5, description="ZIP code")
    lat: float = Field(..., ge=47.0, le=48.0, description="Latitude")
    long: float = Field(..., ge=-123.0, le=-121.0, description="Longitude")
    sqft_living15: int = Field(..., ge=0, description="Square footage of living space in 2015")
    sqft_lot15: int = Field(..., ge=0, description="Square footage of lot in 2015")

class MinimalFeatureRequest(BaseModel):
    bedrooms: int = Field(..., ge=0, description="Number of bedrooms")
    bathrooms: float = Field(..., ge=0, description="Number of bathrooms")
    sqft_living: int = Field(..., ge=0, description="Square footage of living space")
    sqft_lot: int = Field(..., ge=0, description="Square footage of lot")
    floors: float = Field(..., ge=0, description="Number of floors")
    sqft_above: int = Field(..., ge=0, description="Square footage above ground")
    sqft_basement: int = Field(..., ge=0, description="Square footage of basement")
    zipcode: str = Field(..., min_length=5, max_length=5, description="ZIP code")

class PredictionResponse(BaseModel):
    prediction: float = Field(..., description="Predicted house price")
    confidence: Optional[float] = Field(None, description="Prediction confidence score")
    model_version: str = Field(..., description="Model version identifier")
    features_used: List[str] = Field(..., description="List of features used for prediction")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    metadata: Dict = Field(..., description="Additional metadata")