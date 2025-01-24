import pytest
from unittest.mock import patch, MagicMock

from app.models import User  # Import your models
from app.services import create_user, check_existing_user




class MockForm:
    """
    A simple mock form object that mimics WTForms behavior:
    form.username.data, form.email.data, form.password.data
    """
    def __init__(self, username, email, password):
        self.username = MockField(username)
        self.email = MockField(email)
        self.password = MockField(password)

class MockField:
    """
    A mock field class that just stores data in self.data
    """
    def __init__(self, data):
        self.data = data

class TestUserServices:
    def test_create_user(app):
        # Arrange: A mock registration form
        form = MockForm(username="test_new_user", email="test@example.com", password="secret123")

        # Act: We call create_user
        user = create_user(form)

        # Assert: A User should be added to the database
        assert user.id is not None, "User should have an ID after creation"
        assert user.username == "test_new_user"
        assert user.email == "test@example.com"
        assert user.password_hash != "secret123"  # password is hashed


    def test_check_existing_user(app, existing_user):
        # Arrange: A user already in the DB
            # created by the existing_user fixture

        # Act: We check for that user
        found_user = check_existing_user("test_user")

        # Assert: We should get the user object back
        assert found_user is not None
        assert found_user.username == "test_user"


    def test_check_non_existent_user(app):
        # Act: We look for a user that doesn't exist
        found_user = check_existing_user("ghost")

        # Assert: We should get None
        assert found_user is None
