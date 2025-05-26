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

app.add_middleware(
    CORSMiddleware,
    allow_origins=configs.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
async def root() -> dict[str, str]:

    return {"message": f"{configs.PROJECT_NAME}"}


app.include_router(v1_routers, prefix=configs.API_V1_STR)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
