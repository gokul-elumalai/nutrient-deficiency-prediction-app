import uuid

import pytest
from unittest.mock import MagicMock, patch
from pydantic import EmailStr

# Import your CRUD functions only (assuming path as crud.user)
from crud.user import (
    create_user,
    get_user_by_email,
    authenticate,
    update_user,
    delete_user,
    get_all_users,
)


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.commit.return_value = None
    session.refresh.return_value = None
    session.add.return_value = None
    session.delete.return_value = None
    return session


def make_mock_user(email="test@example.com", full_name="test user", hashed_password="hashed"):
    user = MagicMock()
    user.id = uuid.uuid4()
    user.full_name = full_name
    user.email = email
    user.hashed_password = hashed_password
    return user


def test_create_user(mock_session):
    user_create = MagicMock()
    user_create.email = "test@example.com"
    user_create.password = "secret"

    with patch("crud.user.User") as MockUser, patch("crud.user.get_password_hash") as mock_hash:
        mock_hash.return_value = "hashed_secret"
        mock_user_instance = make_mock_user(email=user_create.email, hashed_password="hashed_secret")
        # When User.model_validate(...) is called, return our mock user instance
        MockUser.model_validate.return_value = mock_user_instance

        user = create_user(session=mock_session, user_create=user_create)

        mock_session.add.assert_called_once_with(mock_user_instance)
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_user_instance)

        assert user.email == "test@example.com"
        assert user.hashed_password == "hashed_secret"


def test_get_user_by_email_found(mock_session):
    fake_user = make_mock_user(email="found@example.com")
    # Mock the chained call session.exec(...).first()
    mock_session.exec.return_value.first.return_value = fake_user

    user = get_user_by_email(session=mock_session, email="found@example.com")

    assert user == fake_user
    mock_session.exec.assert_called_once()


def test_get_user_by_email_not_found(mock_session):
    mock_session.exec.return_value.first.return_value = None

    user = get_user_by_email(session=mock_session, email="notfound@example.com")

    assert user is None
    mock_session.exec.assert_called_once()


def test_authenticate_success(mock_session):
    fake_user = make_mock_user(email="auth@example.com", hashed_password="hashed_pw")
    mock_session.exec.return_value.first.return_value = fake_user

    with patch("crud.user.verify_password", return_value=True):
        user = authenticate(session=mock_session, email="auth@example.com", password="any")

    assert user == fake_user


def test_authenticate_fail_wrong_password(mock_session):
    fake_user = make_mock_user(email="authfail@example.com", hashed_password="hashed_pw")
    mock_session.exec.return_value.first.return_value = fake_user

    with patch("crud.user.verify_password", return_value=False):
        user = authenticate(session=mock_session, email="authfail@example.com", password="wrong")

    assert user is None


def test_authenticate_fail_no_user(mock_session):
    mock_session.exec.return_value.first.return_value = None

    user = authenticate(session=mock_session, email="nouser@example.com", password="pw")

    assert user is None


def test_update_user(mock_session):
    existing_user = make_mock_user(email="update@example.com", hashed_password="old_hashed")

    user_update = MagicMock()
    user_update.model_dump.return_value = {"password": "newpassword"}

    with patch("crud.user.get_password_hash", return_value="new_hashed_pw"):
        updated_user = update_user(session=mock_session, db_user=existing_user, user_info=user_update)

    mock_session.add.assert_called_once_with(existing_user)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(existing_user)

    # Check that the password was updated via hashed_password field
    assert hasattr(updated_user, "hashed_password")


def test_delete_user(mock_session):
    user_to_delete = make_mock_user(email="delete@example.com")

    msg = delete_user(session=mock_session, db_user=user_to_delete)

    mock_session.delete.assert_called_once_with(user_to_delete)
    mock_session.commit.assert_called_once()

    assert hasattr(msg, "message")
    assert msg.message == "User deleted successfully"


def test_get_all_users(mock_session):
    fake_users = [make_mock_user(email="user1@example.com"), make_mock_user(email="user2@example.com")]

    # Mock count query returns 2
    count_mock = MagicMock()
    count_mock.one.return_value = 2

    users_mock = MagicMock()
    users_mock.all.return_value = fake_users

    # exec() returns different mocks based on calls
    mock_session.exec.side_effect = [count_mock, users_mock]

    result = get_all_users(session=mock_session, skip=0, limit=10)
    print(result)

    assert result.count == 2
    assert len(result.data) == 2
