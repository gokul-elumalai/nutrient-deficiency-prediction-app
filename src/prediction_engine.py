import json
from pathlib import Path

import joblib
from sqlmodel import SQLModel
import pandas as pd
import warnings

from config.config import NUMERIC_FEATURES, BMI

# Suppress all warnings
warnings.filterwarnings("ignore")


class DietPredictor:
    def __init__(self, model_path: str = "ml_model/meal_plan_pipeline.joblib"):
        self.model = self._load_model(model_path)

    @staticmethod
    def _load_model(model_path: str):
        """Load the trained model"""
        model_file = Path(__file__).parent / model_path
        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found at {model_file}")
        return joblib.load(model_file)

    @staticmethod
    def _get_bmi_class(bmi: int) -> str:
        BMI_CLASS = {'underweight': (0, 18.49),
               'normal': (18.5, 24.99),
               'overweight': (25, 29.99),
               'obese': (30, 100)
               }
        for category, rnge in BMI_CLASS.items():
            start, end = rnge

            if start <= bmi <= end:
                return category
        return 'None'

    def _preprocess_input(self, user_details: dict):
        user_details = {k.lower(): v for k, v in user_details.items()}

        record_df = pd.DataFrame([user_details])

        for col in NUMERIC_FEATURES:
            record_df[col] = pd.to_numeric(record_df[col], errors='coerce')

        return record_df

    def predict(self, user_details: SQLModel, food_log_count: int) -> str:
        """Predict diet plan"""
        input_data = json.loads(user_details.json())
        input_data[BMI] = self._get_bmi_class(input_data[BMI])

        # if log count is less go to fallback
        if food_log_count < 21:
            return self._fallback_diet(input_data[BMI])

        pipeline = self.model["pipeline"]
        record = self._preprocess_input(input_data)
        prediction = pipeline.predict(record)[0]

        return prediction

    @staticmethod
    def _fallback_diet(bmi_class: str) -> str:
        fallback_map = {
            "underweight": "Balanced",
            "normal": "Balanced",
            "overweight": "High Protein",
            "obese": "Low Fat"
        }
        return fallback_map.get(bmi_class, "Balanced")


# Singleton instance
diet_predictor = DietPredictor()
