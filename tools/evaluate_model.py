#!/usr/bin/env python3
"""
Model Evaluation Script for House Price Prediction Model

This script evaluates the performance of the trained model by:
1. Loading the trained model and data
2. Performing cross-validation
3. Analyzing feature importance
4. Testing generalization on unseen data
5. Generating performance metrics and visualizations

The script handles the complete ML model evaluation pipeline including:
- Model loading and validation
- Data preprocessing with proper ZIP code handling
- Cross-validation for model stability assessment
- Test set performance evaluation
- Feature importance analysis using correlations
- Generalization testing on unseen examples
- Comprehensive visualization generation
- Detailed evaluation report creation
"""

import json
import pickle
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split

# Suppress warnings for cleaner output during evaluation
warnings.filterwarnings("ignore")

# Configure matplotlib and seaborn for consistent, attractive plotting
plt.style.use("default")  # Use default matplotlib style for clean plots
sns.set_palette("husl")  # Use husl color palette for better color distinction


class ModelEvaluator:
    """
    Comprehensive model evaluation class for house price prediction models.

    This class provides methods to evaluate model performance across multiple dimensions:
    - Cross-validation stability
    - Test set performance metrics
    - Feature importance analysis
    - Generalization capability on unseen data
    - Visualization generation
    - Detailed reporting
    """

    def __init__(self):
        """Initialize the evaluator with empty state variables"""
        # Core model and feature information
        self.model = None  # Trained ML model (pickle-loaded)
        self.features = None  # List of feature names in correct order

        # Training and test data splits
        self.X_train = None  # Training features DataFrame
        self.X_test = None  # Test features DataFrame
        self.y_train = None  # Training target values (prices)
        self.y_test = None  # Test target values (prices)

        # Full dataset (before splitting)
        self.X_full = None  # Complete feature matrix
        self.y_full = None  # Complete target vector

        # Storage for evaluation results
        self.results = {}  # Dictionary to store all evaluation metrics

    def load_model_and_data(self):
        """
        Load the trained model and prepare data for evaluation.

        This method performs the following steps:
        1. Loads the pickled ML model from disk
        2. Loads the feature list to ensure correct column ordering
        3. Calls the data preparation method to load and merge datasets
        4. Validates that all required files exist

        Returns:
            bool: True if successful, False if any required files are missing
        """
        print("📊 Loading model and data...")

        try:
            # Load the trained model (pickle format) and feature configuration
            model_path = Path("model/model.pkl")  # Serialized ML model
            features_path = Path("model/model_features.json")  # Feature names and order

            # Validate that both required files exist before proceeding
            if not model_path.exists() or not features_path.exists():
                print("❌ Model files not found. Please run create_model.py first.")
                return False

            # Load the trained model from pickle file
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)

            # Load the feature list to ensure correct column ordering during prediction
            with open(features_path, "r") as f:
                self.features = json.load(f)

            print("✅ Model loaded successfully")
            print(f"   Features: {len(self.features)}")
            print(f"   Model type: {type(self.model).__name__}")

            # Load and prepare the training data with demographics
            self._load_and_prepare_data()
            return True

        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False

    def _load_and_prepare_data(self):
        """
        Load and prepare data for evaluation by merging house sales data with demographics.

        This method:
        1. Loads house sales data with basic features (bedrooms, bathrooms, etc.)
        2. Loads ZIP code demographics data (income, education, housing values)
        3. Merges datasets on ZIP code to create enriched feature set
        4. Splits data into training (80%) and test (20%) sets
        5. Ensures ZIP codes are handled as strings to prevent type mismatches

        The resulting dataset combines structural house features with neighborhood
        demographic characteristics for comprehensive model evaluation.
        """
        try:
            # Load house sales data with essential features only
            # Note: We only load the features that are available in the unseen examples
            sales_data = pd.read_csv(
                "data/kc_house_data.csv",
                usecols=[
                    "price",
                    "bedrooms",
                    "bathrooms",
                    "sqft_living",
                    "sqft_lot",
                    "floors",
                    "sqft_above",
                    "sqft_basement",
                    "zipcode",
                ],
                dtype={"zipcode": str},
            )  # Critical: ensure ZIP codes are strings

            # Load ZIP code demographics data (income, education, housing characteristics)
            demographics = pd.read_csv(
                "data/zipcode_demographics.csv", dtype={"zipcode": str}
            )

            # Merge house data with demographics on ZIP code
            # 'left' join ensures we keep all house sales even if demographics missing
            merged_data = sales_data.merge(demographics, how="left", on="zipcode").drop(
                columns="zipcode"
            )

            # Separate target variable (price) from features
            self.y_full = merged_data.pop("price")  # Extract price column
            self.X_full = merged_data  # Remaining columns become features

            # Split data into training (80%) and test (20%) sets with fixed random seed
            # This ensures reproducible results across different runs
            self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                self.X_full, self.y_full, test_size=0.2, random_state=42
            )

            print("✅ Data loaded successfully")
            print(f"   Training set: {len(self.X_train)} samples")
            print(f"   Test set: {len(self.X_test)} samples")
            print(f"   Total features: {len(self.X_full.columns)}")

        except Exception as e:
            print(f"❌ Error preparing data: {e}")
            raise

    def evaluate_cross_validation(self):
        """
        Perform cross-validation to assess model stability and generalization.

        This method uses 5-fold cross-validation to:
        1. Split training data into 5 equal parts
        2. Train model on 4 parts, validate on 1 part (5 times total)
        3. Calculate RMSE for each fold
        4. Compute mean and standard deviation of RMSE scores

        Cross-validation helps identify if the model is stable across different
        data subsets and provides a more robust estimate of model performance.
        """
        print("\n🔄 Performing cross-validation...")

        try:
            # Perform 5-fold cross-validation using negative mean squared error
            # sklearn returns negative MSE, so we convert to positive RMSE
            cv_scores = cross_val_score(
                self.model,
                self.X_train,
                self.y_train,
                cv=5,
                scoring="neg_mean_squared_error",
            )

            # Convert negative MSE scores to positive RMSE values
            # RMSE = sqrt(MSE) and provides interpretable dollar amounts
            rmse_scores = np.sqrt(-cv_scores)

            # Store cross-validation results for later analysis and reporting
            self.results["cv_rmse_mean"] = (
                rmse_scores.mean()
            )  # Average performance across folds
            self.results["cv_rmse_std"] = (
                rmse_scores.std()
            )  # Consistency measure (lower = more stable)
            self.results["cv_rmse_scores"] = (
                rmse_scores.tolist()
            )  # Individual fold scores

            print("✅ Cross-validation completed")
            print(f"   Mean RMSE: ${rmse_scores.mean():,.2f}")
            print(f"   Std RMSE: ${rmse_scores.std():,.2f}")
            print(f"   CV scores: {rmse_scores.tolist()}")

        except Exception as e:
            print(f"❌ Error in cross-validation: {e}")

    def evaluate_test_set_performance(self):
        """
        Evaluate model performance on the held-out test set.

        This method provides a realistic assessment of how well the model
        will perform on unseen data by:
        1. Making predictions on the test set (never seen during training)
        2. Computing multiple performance metrics for comprehensive evaluation
        3. Storing results for later analysis and reporting

        The test set performance is the most important metric as it represents
        true generalization capability on unseen data.
        """
        print("\n📈 Evaluating test set performance...")

        try:
            # Generate predictions on the test set using the trained model
            y_pred = self.model.predict(self.X_test)

            # Calculate comprehensive performance metrics
            mse = mean_squared_error(self.y_test, y_pred)  # Mean Squared Error
            rmse = np.sqrt(mse)  # Root Mean Squared Error (in dollars)
            mae = mean_absolute_error(
                self.y_test, y_pred
            )  # Mean Absolute Error (in dollars)
            r2 = r2_score(
                self.y_test, y_pred
            )  # R-squared (coefficient of determination)

            # Calculate Mean Absolute Percentage Error for relative performance assessment
            mape = np.mean(np.abs((self.y_test - y_pred) / self.y_test)) * 100

            # Store all test metrics for comprehensive reporting
            self.results["test_metrics"] = {
                "mse": mse,  # Raw squared error (harder to interpret)
                "rmse": rmse,  # Error in dollars (most interpretable)
                "mae": mae,  # Average absolute error in dollars
                "r2": r2,  # Proportion of variance explained (0-1, higher is better)
                "mape": mape,  # Average percentage error (easier to compare across price ranges)
            }

            print("✅ Test set evaluation completed")
            print(f"   RMSE: ${rmse:,.2f}")
            print(f"   MAE: ${mae:,.2f}")
            print(f"   R²: {r2:.4f}")
            print(f"   MAPE: {mape:.2f}%")

        except Exception as e:
            print(f"❌ Error in test set evaluation: {e}")

    def analyze_feature_importance(self):
        """
        Analyze feature importance using correlation analysis.

        Since K-Nearest Neighbors doesn't provide built-in feature importance,
        we use correlation analysis as a proxy to understand which features
        have the strongest linear relationship with house prices.

        This method:
        1. Calculates absolute correlation between each feature and target (price)
        2. Sorts features by correlation strength (highest first)
        3. Identifies the most predictive features for house pricing
        4. Provides insights for feature engineering and model interpretation

        Note: Correlation measures linear relationships only. Non-linear
        relationships may not be captured by this analysis.
        """
        print("\n🔍 Analyzing feature importance...")

        try:
            # Calculate absolute correlation between each feature and the target variable (price)
            # We use absolute values since both positive and negative correlations are important
            # Higher absolute correlation indicates stronger predictive power
            correlations = (
                self.X_full.corrwith(self.y_full).abs().sort_values(ascending=False)
            )

            # Store correlations for later analysis and visualization
            self.results["feature_correlations"] = correlations.to_dict()

            print("✅ Feature importance analysis completed")
            print("   Top 10 features by correlation with price:")
            # Display top 10 most correlated features with formatted output
            for i, (feature, corr) in enumerate(correlations.head(10).items(), 1):
                print(f"   {i:2d}. {feature:20s}: {corr:.4f}")

        except Exception as e:
            print(f"❌ Error in feature importance analysis: {e}")

    def test_generalization_on_unseen_data(self):
        """
        Test model generalization capability on completely unseen examples.

        This method evaluates how well the trained model performs on new data
        that was never seen during training or validation. It's a critical
        test of real-world deployment readiness.

        The process:
        1. Loads examples from future_unseen_examples.csv (simulated new houses)
        2. Ensures ZIP codes are properly handled as 5-digit strings
        3. Merges basic house features with ZIP code demographics
        4. Fills any missing features with default values (0.0)
        5. Makes predictions and tracks success/failure rates

        This test validates that the model can handle real-world data
        with the same feature structure and demographic enrichment.
        """
        print("\n🔮 Testing generalization on unseen data...")

        try:
            # Load unseen examples with explicit ZIP code type specification
            # This prevents pandas from inferring ZIP codes as floats
            unseen_data = pd.read_csv(
                "data/future_unseen_examples.csv", dtype={"zipcode": str}
            )

            # Load demographics data for ZIP code enrichment
            demographics = pd.read_csv(
                "data/zipcode_demographics.csv", dtype={"zipcode": str}
            )
            print(f"   Demographics data loaded: {len(demographics)} ZIP codes")
            print(
                f"   Sample ZIP codes in demographics: {demographics['zipcode'].head(5).tolist()}"
            )

            # Process each example individually to handle any data quality issues
            predictions = []
            actual_features_used = []

            # Test first 10 examples to avoid overwhelming output
            for idx, row in unseen_data.head(10).iterrows():
                try:
                    # Extract basic structural features available in unseen examples
                    basic_features = {
                        "bedrooms": row["bedrooms"],
                        "bathrooms": row["bathrooms"],
                        "sqft_living": row["sqft_living"],
                        "sqft_lot": row["sqft_lot"],
                        "floors": row["floors"],
                        "sqft_above": row["sqft_above"],
                        "sqft_basement": row["sqft_basement"],
                    }

                    # Clean and validate ZIP code format
                    zipcode = str(row["zipcode"]).strip()
                    # Handle edge case where ZIP code might have '.0' suffix from float conversion
                    if zipcode.endswith(".0"):
                        zipcode = zipcode[
                            :-2
                        ]  # Remove '.0' suffix to get clean 5-digit string

                    print(f"   Processing ZIP: '{zipcode}'")

                    # Look up demographics for this ZIP code
                    zip_demographics = demographics[demographics["zipcode"] == zipcode]

                    if not zip_demographics.empty:
                        # Successfully found demographics - merge with basic features
                        features_dict = {
                            **basic_features,
                            **zip_demographics.iloc[0].to_dict(),
                        }
                        features_dict.pop(
                            "zipcode", None
                        )  # Remove ZIP code from feature set

                        # Create DataFrame for model prediction
                        features_df = pd.DataFrame([features_dict])

                        # Fill any missing features that the model expects with default values
                        # This ensures the feature matrix has the correct shape
                        missing_features = set(self.features) - set(features_df.columns)
                        for feature in missing_features:
                            features_df[feature] = 0.0

                        # Ensure features are in the exact order the model expects
                        features_df = features_df[self.features]

                        # Make prediction using the trained model
                        prediction = self.model.predict(features_df)[0]
                        predictions.append(prediction)
                        actual_features_used.append(list(features_df.columns))

                    else:
                        # No demographics found for this ZIP code
                        print(f"   ⚠️  No demographics found for ZIP {zipcode}")
                        predictions.append(None)
                        actual_features_used.append([])

                except Exception as e:
                    # Handle any errors during individual example processing
                    print(f"   ❌ Error processing example {idx}: {e}")
                    predictions.append(None)
                    actual_features_used.append([])

            # Store generalization test results for later analysis
            self.results["unseen_predictions"] = {
                "predictions": predictions,  # List of predicted prices (or None if failed)
                "features_used": actual_features_used,  # Features used for each prediction
                "examples_processed": len(predictions),  # Total examples attempted
            }

            # Calculate and display generalization test summary
            valid_predictions = [p for p in predictions if p is not None]
            if valid_predictions:
                print("✅ Generalization test completed")
                print(f"   Examples processed: {len(predictions)}")
                print(f"   Valid predictions: {len(valid_predictions)}")
                print(f"   Average prediction: ${np.mean(valid_predictions):,.2f}")
                print(
                    f"   Prediction range: ${np.min(valid_predictions):,.2f} - ${np.max(valid_predictions):,.2f}"
                )
            else:
                print("❌ No valid predictions generated")

        except Exception as e:
            print(f"❌ Error in generalization test: {e}")

    def generate_visualizations(self):
        """
        Generate comprehensive performance visualizations for model evaluation.

        This method creates a 2x2 grid of plots that provide insights into:
        1. Cross-validation stability (RMSE across folds)
        2. Feature importance ranking (top correlations)
        3. Prediction accuracy (predicted vs actual prices)
        4. Error analysis (residuals distribution)

        All plots are saved as a single high-resolution image for easy sharing
        and inclusion in reports or presentations.
        """
        print("\n📊 Generating visualizations...")

        try:
            # Create output directory for evaluation results
            output_dir = Path("evaluation_results")
            output_dir.mkdir(exist_ok=True)

            # Create a 2x2 subplot layout for comprehensive visualization
            plt.figure(figsize=(10, 6))

            # 1. Cross-validation RMSE scores across folds
            cv_scores = self.results.get("cv_rmse_scores", [])
            if cv_scores:
                plt.subplot(2, 2, 1)
                # Plot individual fold scores with connecting lines
                plt.plot(range(1, len(cv_scores) + 1), cv_scores, "bo-", markersize=8)
                # Add horizontal line showing mean performance
                plt.axhline(
                    y=np.mean(cv_scores),
                    color="r",
                    linestyle="--",
                    label=f"Mean: ${np.mean(cv_scores):,.0f}",
                )
                plt.xlabel("Cross-Validation Fold")
                plt.ylabel("RMSE ($)")
                plt.title("Cross-Validation RMSE Scores")
                plt.legend()
                plt.grid(True, alpha=0.3)

            # 2. Top 10 feature correlations (feature importance proxy)
            if "feature_correlations" in self.results:
                plt.subplot(2, 2, 2)
                correlations = pd.Series(self.results["feature_correlations"])
                top_features = correlations.head(
                    10
                )  # Show top 10 most correlated features

                # Create horizontal bar chart for easy feature name reading
                plt.barh(range(len(top_features)), top_features.values)
                plt.yticks(range(len(top_features)), top_features.index)
                plt.xlabel("Absolute Correlation with Price")
                plt.title("Top 10 Feature Correlations")
                plt.grid(True, alpha=0.3)

            # 3. Test set predictions vs actual values (scatter plot)
            if "test_metrics" in self.results:
                plt.subplot(2, 2, 3)
                # Generate predictions on test set for comparison
                y_pred = self.model.predict(self.X_test)

                # Create scatter plot of predicted vs actual prices
                plt.scatter(self.y_test, y_pred, alpha=0.6, s=20)

                # Add perfect prediction line (y=x) for reference
                min_price, max_price = self.y_test.min(), self.y_test.max()
                plt.plot([min_price, max_price], [min_price, max_price], "r--", lw=2)

                plt.xlabel("Actual Price ($)")
                plt.ylabel("Predicted Price ($)")
                plt.title("Test Set: Predicted vs Actual Prices")
                plt.grid(True, alpha=0.3)

            # 4. Residuals analysis (errors vs predictions)
            if "test_metrics" in self.results:
                plt.subplot(2, 2, 4)
                # Calculate residuals (actual - predicted)
                residuals = self.y_test - y_pred

                # Plot residuals against predicted values to check for patterns
                plt.scatter(y_pred, residuals, alpha=0.6, s=20)

                # Add horizontal line at y=0 (perfect prediction)
                plt.axhline(y=0, color="r", linestyle="--")

                plt.xlabel("Predicted Price ($)")
                plt.ylabel("Residuals ($)")
                plt.title("Residuals: Errors vs Predictions")
                plt.grid(True, alpha=0.3)

            # Adjust subplot spacing and save high-resolution figure
            plt.tight_layout()
            plt.savefig(
                output_dir / "model_evaluation.png", dpi=300, bbox_inches="tight"
            )
            print(f"✅ Visualizations saved to {output_dir / 'model_evaluation.png'}")

        except Exception as e:
            print(f"❌ Error generating visualizations: {e}")

    def generate_report(self):
        """
        Generate a comprehensive, human-readable evaluation report.

        This method creates a detailed text report that includes:
        - Model metadata and configuration
        - Cross-validation performance metrics
        - Test set evaluation results
        - Feature importance rankings
        - Generalization test outcomes
        - Performance assessments and recommendations

        The report is saved to disk and also printed to console for immediate
        review. It serves as a permanent record of the evaluation session.
        """
        print("\n📋 Generating evaluation report...")

        try:
            # Create output directory for evaluation results
            output_dir = Path("evaluation_results")
            output_dir.mkdir(exist_ok=True)

            # Build report content as a list of strings
            report = []
            report.append("=" * 60)
            report.append("HOUSE PRICE PREDICTION MODEL EVALUATION REPORT")
            report.append("=" * 60)
            report.append("")

            # Section 1: Model Information and Configuration
            report.append("MODEL INFORMATION:")
            report.append("-" * 30)
            report.append(f"Model Type: {type(self.model).__name__}")
            report.append(f"Features Used: {len(self.features)}")
            report.append(f"Training Samples: {len(self.X_train)}")
            report.append(f"Test Samples: {len(self.X_test)}")
            report.append("")

            # Cross-validation results
            if "cv_rmse_mean" in self.results:
                report.append("CROSS-VALIDATION RESULTS:")
                report.append("-" * 30)
                report.append(f"Mean RMSE: ${self.results['cv_rmse_mean']:,.2f}")
                report.append(f"Std RMSE: ${self.results['cv_rmse_std']:,.2f}")
                report.append(
                    f"CV Scores: {[f'${score:,.0f}' for score in self.results['cv_rmse_scores']]}"
                )
                report.append("")

            # Test set performance
            if "test_metrics" in self.results:
                metrics = self.results["test_metrics"]
                report.append("TEST SET PERFORMANCE:")
                report.append("-" * 30)
                report.append(f"RMSE: ${metrics['rmse']:,.2f}")
                report.append(f"MAE: ${metrics['mae']:,.2f}")
                report.append(f"R² Score: {metrics['r2']:.4f}")
                report.append(f"MAPE: {metrics['mape']:.2f}%")
                report.append("")

            # Feature importance
            if "feature_correlations" in self.results:
                report.append("TOP 10 FEATURES BY CORRELATION:")
                report.append("-" * 30)
                correlations = pd.Series(self.results["feature_correlations"])
                for i, (feature, corr) in enumerate(correlations.head(10).items(), 1):
                    report.append(f"{i:2d}. {feature:20s}: {corr:.4f}")
                report.append("")

            # Generalization results
            if "unseen_predictions" in self.results:
                unseen = self.results["unseen_predictions"]
                report.append("GENERALIZATION TEST RESULTS:")
                report.append("-" * 30)
                report.append(f"Examples Processed: {unseen['examples_processed']}")
                valid_preds = [p for p in unseen["predictions"] if p is not None]
                if valid_preds:
                    report.append(f"Valid Predictions: {len(valid_preds)}")
                    report.append(f"Average Prediction: ${np.mean(valid_preds):,.2f}")
                    report.append(
                        f"Prediction Range: ${np.min(valid_preds):,.2f} - ${np.max(valid_preds):,.2f}"
                    )
                report.append("")

            # Model assessment
            report.append("MODEL ASSESSMENT:")
            report.append("-" * 30)

            if "test_metrics" in self.results:
                r2 = self.results["test_metrics"]["r2"]
                mape = self.results["test_metrics"]["mape"]

                if r2 > 0.8:
                    report.append("✅ R² Score: EXCELLENT (> 0.8)")
                elif r2 > 0.6:
                    report.append("✅ R² Score: GOOD (0.6 - 0.8)")
                elif r2 > 0.4:
                    report.append("⚠️  R² Score: FAIR (0.4 - 0.6)")
                else:
                    report.append("❌ R² Score: POOR (< 0.4)")

                if mape < 10:
                    report.append("✅ MAPE: EXCELLENT (< 10%)")
                elif mape < 20:
                    report.append("✅ MAPE: GOOD (10% - 20%)")
                elif mape < 30:
                    report.append("⚠️  MAPE: FAIR (20% - 30%)")
                else:
                    report.append("❌ MAPE: POOR (> 30%)")

            # Save report
            report_path = output_dir / "evaluation_report.txt"
            with open(report_path, "w") as f:
                f.write("\n".join(report))

            print(f"✅ Report saved to {report_path}")

            # Print report to console
            print("\n" + "\n".join(report))

        except Exception as e:
            print(f"❌ Error generating report: {e}")

    def run_full_evaluation(self):
        """
        Execute the complete model evaluation pipeline.

        This method orchestrates the entire evaluation process by calling
        each evaluation step in sequence. It provides a single entry point
        for comprehensive model assessment.

        The pipeline includes:
        1. Model and data loading
        2. Cross-validation assessment
        3. Test set performance evaluation
        4. Feature importance analysis
        5. Generalization testing on unseen data
        6. Visualization generation
        7. Comprehensive report creation

        All results are automatically saved to the evaluation_results/ directory.
        """
        print("🚀 Starting comprehensive model evaluation...")
        print("=" * 60)

        # Step 1: Load the trained model and prepare evaluation data
        if not self.load_model_and_data():
            return

        # Step 2: Run all evaluation components in sequence
        self.evaluate_cross_validation()  # Assess model stability
        self.evaluate_test_set_performance()  # Evaluate on held-out test set
        self.analyze_feature_importance()  # Identify key predictive features
        self.test_generalization_on_unseen_data()  # Test real-world readiness
        self.generate_visualizations()  # Create performance plots
        self.generate_report()  # Generate detailed report

        print("\n🎉 Model evaluation completed successfully!")
        print("📁 Results saved to 'evaluation_results/' directory")


def main():
    """
    Main entry point for the model evaluation script.

    This function creates a ModelEvaluator instance and runs the complete
    evaluation pipeline. It's called when the script is executed directly
    from the command line.

    Usage:
        python tools/evaluate_model.py
    """
    evaluator = ModelEvaluator()
    evaluator.run_full_evaluation()


if __name__ == "__main__":
    """
    Script execution guard - only run main() if this file is executed directly.
    This allows the script to be imported as a module without automatically
    running the evaluation.
    """
    main()
