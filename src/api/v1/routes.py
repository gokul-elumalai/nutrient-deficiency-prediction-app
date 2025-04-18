from fastapi import APIRouter


from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.user import router as user_router
from api.v1.endpoints.food_log import router as food_log_router
from api.v1.endpoints.user_details import router as user_details_router
from api.v1.endpoints.diet_recommendation import router as diet_recommendation_router

routers = APIRouter()
router_list = [auth_router, user_router, food_log_router, user_details_router, diet_recommendation_router]

for router in router_list:
    routers.tags.append("v1")
    routers.include_router(router)
