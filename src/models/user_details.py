import uuid
from typing import Optional, Literal, Annotated
from sqlmodel import SQLModel, Field, Relationship
from pydantic import validator, field_validator
from enum import Enum


# ---- Enums for Categorical Fields ----
class Gender(str, Enum):
    FEMALE = "Female"
    MALE = "Male"
    OTHER = "Other"


class ChronicDisease(str, Enum):
    NA = "NA"
    DIABETES = "Diabetes"
    HEART_DISEASE = "Heart Disease"
    HYPERTENSION = "Hypertension"
    OBESITY = "Obesity"


class GeneticRiskFactor(str, Enum):
    NO = "No"
    YES = "Yes"


class Allergy(str, Enum):
    NA = "NA"
    LACTOSE = "Lactose Intolerance"
    NUT = "Nut Allergy"
    GLUTEN = "Gluten Intolerance"


class AlcoholConsumption(str, Enum):
    NO = "No"
    YES = "Yes"


class SmokingHabit(str, Enum):
    NO = "No"
    YES = "Yes"


class DietaryHabit(str, Enum):
    REGULAR = "Regular"
    KETO = "Keto"
    VEGETARIAN = "Vegetarian"
    VEGAN = "Vegan"


class PreferredCuisine(str, Enum):
    INDIAN = "Indian"
    ASIAN = "Asian"
    WESTERN = "Western"
    MEDITERRANEAN = "Mediterranean"


class FoodAversion(str, Enum):
    SPICY = "Spicy"
    SWEET = "Sweet"
    SALTY = "Salty"
    NA = "NA"


# ---- Main Model ----
class UserDetailsBase(SQLModel):
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[Gender] = Field(None)
    height_cm: Optional[float] = Field(None, gt=0, le=300)  # in cm
    weight_kg: Optional[float] = Field(None, gt=0, le=500)  # in kg
    bmi: Optional[float] = Field(None, gt=0, le=100)  # calculated field

    # Health Metrics
    chronic_disease: ChronicDisease = Field(default=ChronicDisease.NA)
    cholesterol_level: Optional[float] = Field(None, ge=0)  # mg/dL
    blood_sugar_level: Optional[float] = Field(None, ge=0)  # mg/dL
    blood_pressure_systolic: Optional[int] = Field(None, ge=0, le=300)  # mmHg
    blood_pressure_diastolic: Optional[int] = Field(None, ge=0, le=200)  # mmHg

    # Nutritional Intake
    calorie_intake: Optional[float] = Field(None, ge=0)  # kcal/day
    protein_intake: Optional[float] = Field(None, ge=0)  # g/day
    fat_intake: Optional[float] = Field(None, ge=0)  # g/day
    carbohydrate_intake: Optional[float] = Field(None, ge=0)  # g/day

    # Lifestyle Factors
    genetic_risk_factor: GeneticRiskFactor = Field(default=GeneticRiskFactor.NO)
    allergies: Allergy = Field(default=Allergy.NA)
    daily_steps: Optional[int] = Field(None, ge=0)
    exercise_frequency: Optional[int] = Field(None, ge=0, le=7)  # times/week
    sleep_hours: Optional[float] = Field(None, gt=0, le=24)  # hours/day
    alcohol_consumption: AlcoholConsumption = Field(default=AlcoholConsumption.NO)
    smoking_habit: SmokingHabit = Field(default=SmokingHabit.NO)

    # Dietary Preferences
    dietary_habits: DietaryHabit = Field(default=DietaryHabit.REGULAR)
    preferred_cuisine: PreferredCuisine = Field(default=PreferredCuisine.WESTERN)
    food_aversions: FoodAversion = Field(default=FoodAversion.NA)

    # BMI Calculation (example validator)
    @field_validator('bmi', mode='before')
    def calculate_bmi(cls, v, values):
        if v is not None:
            return v
        data = values.data
        if 'height_cm' in data and 'weight_kg' in data:
            if data['height_cm'] and data['weight_kg']:
                height_m = data['height_cm'] / 100
                return round(data['weight_kg'] / (height_m ** 2), 1)
        return None


class UserDetails(UserDetailsBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")

    # Relationship
    user: "User" = Relationship(back_populates="user_details")


# Create/Update Models
class UserDetailsCreate(UserDetailsBase):
    pass


class UserDetailsUpdate(SQLModel):
    # All fields optional for PATCH
    age: Optional[int] = None
    gender: Optional[Gender] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    # ... (include all other fields as optional)


class UserDetailsPublic(UserDetailsBase):
    id: uuid.UUID
    user_id: uuid.UUID
