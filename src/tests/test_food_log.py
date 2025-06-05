import uuid
import pytest
from unittest.mock import MagicMock, patch
from models.food_log import FoodLogCreate
from crud.food_log import create_food_log


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.commit.return_value = None
    session.refresh.return_value = None
    session.add.return_value = None
    return session


def make_mock_food_log(id_=None, user_id=None, food="Apple", calories=50):
    obj = MagicMock()
    obj.id = id_ or uuid.uuid4()
    obj.user_id = user_id or uuid.uuid4()
    obj.food = food
    obj.calories = calories
    return obj


def test_create_food_log(mock_session):
    user_id = uuid.uuid4()
    food_log_data = FoodLogCreate(
        log_date="2025-06-01",
        food="Banana",
        meal_type="breakfast",
        calories=100,
        carbs=27,
        protein=1.3,
        fat=0.3
    )

    # Patch FoodLog.model_validate to return a mock FoodLog instance
    with patch("crud.food_log.FoodLog") as MockFoodLog, \
         patch("crud.food_log.update_user_nutrition_summary") as mock_update_summary:

        mock_food_log_instance = make_mock_food_log(user_id=user_id, food="Banana", calories=100)
        MockFoodLog.model_validate.return_value = mock_food_log_instance

        result = create_food_log(session=mock_session, food_log=food_log_data, user_id=user_id)

        # Ensure model_validate was called with the FoodLogCreate and user_id in update
        MockFoodLog.model_validate.assert_called_once_with(food_log_data, update={"user_id": user_id})

        # Assert session methods called correctly
        mock_session.add.assert_called_once_with(mock_food_log_instance)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_food_log_instance)

        # update_user_nutrition_summary should be called once with session and user_id
        mock_update_summary.assert_called_once_with(mock_session, user_id)

        # Result should be the mocked FoodLog instance
        assert result == mock_food_log_instance
