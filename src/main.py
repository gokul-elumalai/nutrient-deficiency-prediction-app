from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
from utils.recommendations import get_food_recommendations
from core.config import configs

app = FastAPI()

# model = joblib.load("model/nutrient_model.pkl")
# features = joblib.load("model/model_features.pkl")
# targets = [f"{f}_deficient" for f in ['protein', 'iron', 'calcium', 'vitamin_c', 'fiber']]


class NutritionInput(BaseModel):
    calories: float
    protein: float
    fat: float
    carbs: float
    fiber: float
    iron: float
    calcium: float
    vitamin_c: float


@app.post("/predict")
def predict_deficiencies(data: NutritionInput):
    input_array = np.array([[getattr(data, f) for f in features]])
    prediction = model.predict(input_array)[0]
    pred_dict = dict(zip(targets, prediction))
    recs = get_food_recommendations(pred_dict)
    return {
        "deficiencies": [k for k, v in pred_dict.items() if v == 1],
        "recommendations": recs
    }

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": f"{configs.PROJECT_NAME}"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
