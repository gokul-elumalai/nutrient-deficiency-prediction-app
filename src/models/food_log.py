import uuid
from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from pydantic import validator


# Base Models
class FoodLogBase(SQLModel):
    log_date: date = Field(index=True, alias='date')
    food: str = Field(max_length=100)
    meal_type: str = Field(max_length=20)  # e.g., "breakfast", "lunch", "dinner", "snack"
    calories: float = Field(ge=0)
    carbs: float = Field(ge=0, default=0)
    protein: float = Field(ge=0, default=0)
    fat: float = Field(ge=0, default=0)

    # Micronutrients (optional fields)
    sugar: Optional[float] = Field(default=None, ge=0)
    sodium: Optional[float] = Field(default=None, ge=0)  # in mg
    potassium: Optional[float] = Field(default=None, ge=0)  # in mg
    fiber: Optional[float] = Field(default=None, ge=0)  # in g
    iron: Optional[float] = Field(default=None, ge=0)  # in mg
    calcium: Optional[float] = Field(default=None, ge=0)  # in mg
    cholesterol: Optional[float] = Field(default=None, ge=0)  # in mg
    vitamin_a: Optional[float] = Field(default=None, ge=0)  # in IU
    vitamin_c: Optional[float] = Field(default=None, ge=0)  # in mg
    saturated_fat: Optional[float] = Field(default=None, ge=0)  # in g
    trans_fat: Optional[float] = Field(default=None, ge=0)  # in g
    polyunsaturated_fat: Optional[float] = Field(default=None, ge=0)  # in g
    monounsaturated_fat: Optional[float] = Field(default=None, ge=0)  # in g

    # Validator example
    @validator('meal_type')
    def validate_meal_type(cls, v):
        allowed = ["breakfast", "lunch", "dinner", "snack"]
        if v.lower() not in allowed:
            raise ValueError(f"Meal type must be one of: {', '.join(allowed)}")
        return v.lower()


# Database Model with Relationship
class FoodLog(FoodLogBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")

    # Relationship to User
    user: "User" = Relationship(back_populates="food_logs")  # Circular import fixed below


# Create Model (for POST requests)
class FoodLogCreate(FoodLogBase):
    pass


# Update Model (for PATCH requests)
class FoodLogUpdate(SQLModel):
    date: Optional[date] = None
    food: Optional[str] = None
    meal_type: Optional[str] = None
    calories: Optional[float] = None

    # Include all other fields as optional...

    @validator('meal_type', pre=True, always=True)
    def validate_meal_type_update(cls, v):
        if v is not None:
            return FoodLogBase.validate_meal_type(v)
        return v


# Read Model (for response)
class FoodLogRead(FoodLogBase):
    id: int
    user_id: int


class FoodLogPublic(FoodLogBase):
    id: uuid.UUID


class FoodLogsPublic(SQLModel):
    data: list[FoodLogPublic]
    count: int

# Fix circular import
# from src.models.user import User  # noqa
#
# FoodLog.update_forward_refs(User=User)
