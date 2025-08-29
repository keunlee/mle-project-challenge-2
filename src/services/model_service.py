import json
import logging
import os
import pickle
import threading
from pathlib import Path
from typing import Dict

import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelService:
    def __init__(self):
        self.lock = threading.Lock()
        self.model_path = Path("model/model.pkl")
        self.features_path = Path("model/model_features.json")
        self.model_mtime = None
        self.model = None
        self.features = None
        self.demographics_data = None
        self.model_version = "1.0.0"
        self.load_model()
        self.load_demographics()

    # Load the model and features
    def load_model(self):
        with self.lock:
            if not self.model_path.exists() or not self.features_path.exists():
                logger.error("Model files not found. Please run create_model.py first.")
                raise FileNotFoundError("Model files not found")
            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)
            with open(self.features_path, "r") as f:
                self.features = json.load(f)
            self.model_mtime = os.path.getmtime(self.model_path)
            self.model_version = str(self.model_mtime)
            logger.info(f"Model loaded. Version: {self.model_version}")

    # Reload the model if the file has changed
    def reload_model(self):
        with self.lock:
            current_mtime = os.path.getmtime(self.model_path)
            if current_mtime != self.model_mtime:
                logger.info("Reloading model due to file change...")
                self.load_model()
            else:
                logger.info("Model file unchanged. No reload needed.")

    # Load demographics data
    def load_demographics(self):
        """Load demographics data for ZIP code enrichment"""
        try:
            demographics_path = Path("data/zipcode_demographics.csv")
            if not demographics_path.exists():
                logger.error("Demographics data not found")
                raise FileNotFoundError("Demographics data not found")

            self.demographics_data = pd.read_csv(
                demographics_path, dtype={"zipcode": str}
            )
            logger.info(
                f"Demographics data loaded successfully. Shape: {self.demographics_data.shape}"
            )

        except Exception as e:
            logger.error(f"Error loading demographics data: {e}")
            raise

    # Enrich input data with demographics based on ZIP code
    def enrich_with_demographics(self, zipcode: str) -> Dict:
        """Enrich data with demographic information for a given ZIP code"""
        try:
            zipcode_str = str(zipcode)
            demographics = self.demographics_data[
                self.demographics_data["zipcode"] == zipcode_str
            ]

            if demographics.empty:
                logger.warning(f"No demographics data found for ZIP code: {zipcode}")
                # Return default values if no demographics found
                return {
                    "medn_hshld_incm_amt": 50000.0,
                    "hous_val_amt": 250000.0,
                    "per_urbn": 80.0,
                    "per_sbrbn": 20.0,
                }

            # Return the first (and should be only) row
            return demographics.iloc[0].to_dict()

        except Exception as e:
            logger.error(f"Error enriching demographics for ZIP {zipcode}: {e}")
            return {}

    # Prepare features for model prediction
    def prepare_features(
        self, request_data: Dict, minimal: bool = False
    ) -> pd.DataFrame:
        """Prepare features for model prediction"""
        try:
            if minimal:
                # For minimal features, we need to add missing columns with default values
                # and then enrich with demographics
                features_dict = {
                    "bedrooms": request_data["bedrooms"],
                    "bathrooms": request_data["bathrooms"],
                    "sqft_living": request_data["sqft_living"],
                    "sqft_lot": request_data["sqft_lot"],
                    "floors": request_data["floors"],
                    "sqft_above": request_data["sqft_above"],
                    "sqft_basement": request_data["sqft_basement"],
                }

                # Add demographics
                demographics = self.enrich_with_demographics(request_data["zipcode"])
                features_dict.update(demographics)

            else:
                # Use all features expected by the model
                features_dict = {
                    feature: request_data.get(feature, 0.0) for feature in self.features
                }

                # Add demographics
                demographics = self.enrich_with_demographics(request_data["zipcode"])
                features_dict.update(demographics)

            # Create DataFrame and ensure correct column order
            features_df = pd.DataFrame([features_dict])

            # Ensure all required features are present
            missing_features = set(self.features) - set(features_df.columns)
            if missing_features:
                logger.warning(
                    f"Missing features: {missing_features}. Adding with default values."
                )
                for feature in missing_features:
                    features_df[feature] = 0.0

            # Select only the features the model expects, in the correct order
            features_df = features_df[self.features]

            return features_df

        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            raise

    # Make prediction using the model
    def predict(self, features_df: pd.DataFrame) -> float:
        """Make prediction using the loaded model"""
        try:
            prediction = self.model.predict(features_df)[0]
            return float(prediction)
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            raise
