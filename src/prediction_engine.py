import json
from pathlib import Path

import joblib
from sqlmodel import SQLModel
import pandas as pd


class DietPredictor:
    def __init__(self, model_path: str = "ml_model/meal_plan_pipeline.joblib"):
        self.model = self._load_model(model_path)

    def _load_model(self, model_path: str):
        """Load the trained model"""
        model_file = Path(__file__).parent / model_path
        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found at {model_file}")
        return joblib.load(model_file)

    def _get_bmi_class(self, bmi: int) -> str:
        BMI = {'underweight': (0, 18.49),
               'normal': (18.5, 24.99),
               'overweight': (25, 29.99),
               'obese': (30, 100)
               }
        for category, rnge in BMI.items():
            start, end = rnge

            if bmi >= start and bmi <= end:
                return category
        return 'None'

    def _preprocess_input(self, user_details: dict):
        user_details = {k.lower(): v for k, v in user_details.items()}
        user_details['bmi'] = self._get_bmi_class(user_details['bmi'])

        record_df = pd.DataFrame([user_details])

        NUM_COLS = ['height_cm', 'weight_kg', 'cholesterol_level', 'blood_sugar_level', 'daily_steps',
                    'exercise_frequency', 'sleep_hours', 'calorie_intake', 'protein_intake',
                    'carbohydrate_intake', 'fat_intake']
        for col in NUM_COLS:
            record_df[col] = pd.to_numeric(record_df[col], errors='coerce')

        return record_df

    def predict(self, user_details: SQLModel) -> str:
        """Predict diet plan"""
        # input_data = self.preprocess_input(user_details)
        pipeline = self.model["pipeline"]
        input_data = json.loads(user_details.json())
        record = self._preprocess_input(input_data)
        prediction = pipeline.predict(record)[0]

        return prediction


# Singleton instance
diet_predictor = DietPredictor()
