from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
from fastapi.middleware.cors import CORSMiddleware

from core import db
from core.security import get_password_hash
from utils.recommendations import get_food_recommendations
from api.v1.routes import routers as v1_routers
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=configs.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
async def root() -> dict[str, str]:
    j = get_password_hash("stringst")
    return {"message": f"{configs.PROJECT_NAME} {j}"}


app.include_router(v1_routers, prefix=configs.API_V1_STR)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
