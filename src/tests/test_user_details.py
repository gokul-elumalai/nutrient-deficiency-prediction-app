import uuid
import pytest
from unittest.mock import MagicMock, patch
from models.user_details import UserDetailsCreate
from models.food_log import FoodLog
from crud.user_details import create_user_details, update_user_nutrition_summary


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.commit.return_value = None
    session.refresh.return_value = None
    session.add.return_value = None
    session.exec.return_value.all.return_value = []
    session.exec.return_value.first.return_value = None
    return session


def make_mock_user_details(id_=None, user_id=None):
    obj = MagicMock()
    obj.id = id_ or uuid.uuid4()
    obj.user_id = user_id or uuid.uuid4()
    obj.calorie_intake = 0
    obj.protein_intake = 0
    obj.fat_intake = 0
    obj.carbohydrate_intake = 0
    return obj


def test_create_user_details(mock_session):
    user_id = uuid.uuid4()
    user_details_data = UserDetailsCreate(
        age=30,
        gender="Male",
        height_cm=175,
        weight_kg=70,
        bmi=22.9,
    )

    with patch("crud.user_details.UserDetails") as MockUserDetails:
        mock_user_details_instance = make_mock_user_details(user_id=user_id)
        MockUserDetails.model_validate.return_value = mock_user_details_instance

        result = create_user_details(session=mock_session, user_details=user_details_data, user_id=user_id)

        MockUserDetails.model_validate.assert_called_once_with(user_details_data, update={"user_id": user_id})
        mock_session.add.assert_called_once_with(mock_user_details_instance)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_user_details_instance)

        assert result == mock_user_details_instance


def test_update_user_nutrition_summary_with_details(mock_session):
    user_id = uuid.uuid4()

    # Mock food log results with dummy nutrition values
    mock_food_log1 = MagicMock(calories=100, protein=5, fat=2, carbs=20)
    mock_food_log2 = MagicMock(calories=200, protein=10, fat=3, carbs=30)

    # Mock the query for food logs
    mock_food_logs = [mock_food_log1, mock_food_log2]
    mock_session.exec.return_value.all.return_value = mock_food_logs

    # Mock user details object to be updated
    mock_user_details = make_mock_user_details(user_id=user_id)
    mock_session.exec.return_value.first.return_value = mock_user_details

    update_user_nutrition_summary(mock_session, user_id)

    # Check sums were correctly assigned
    assert mock_user_details.calorie_intake == 300
    assert mock_user_details.protein_intake == 15
    assert mock_user_details.fat_intake == 5
    assert mock_user_details.carbohydrate_intake == 50

    # Check session methods called properly
    mock_session.add.assert_called_once_with(mock_user_details)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(mock_user_details)


def test_update_user_nutrition_summary_no_details(mock_session):
    user_id = uuid.uuid4()

    # Return food logs but no user details
    mock_session.exec.return_value.all.return_value = []
    mock_session.exec.return_value.first.return_value = None

    # Should not raise and should not call add/commit/refresh
    update_user_nutrition_summary(mock_session, user_id)

    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()
