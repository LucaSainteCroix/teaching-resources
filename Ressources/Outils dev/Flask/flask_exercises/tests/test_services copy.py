# import pytest
# from unittest.mock import patch, MagicMock
# from app.services import create_user, check_existing_user
# from app.models import User
# from werkzeug.security import check_password_hash

# @pytest.fixture
# def mock_form():
#     """
#     This fixture creates a mock form object with 'username.data' and 'password.data'.
#     It's used to simulate the form passed to create_user().
#     """
#     form = MagicMock()
#     form.username.data = "testuser"
#     form.password.data = "testpass"
#     return form


# @patch("app.services.db")  # patch the 'db' import in app.services
# def test_create_user(mock_db, mock_form):
#     """
#     Tests that create_user:
#     1) Hashes the password
#     2) Creates a User with the correct username
#     3) Calls db.session.add and db.session.commit
#     4) Returns the user
#     """
#     # Arrange
#     # Mock the session so we don't commit to a real database
#     mock_session = MagicMock()
#     mock_db.session = mock_session

#     # Act
#     created_user = create_user(mock_form)

#     # Assert
#     # 1. db.session.add should be called with a User object
#     mock_session.add.assert_called_once()
#     added_user = mock_session.add.call_args[0][0]  # The actual user passed to add()
#     assert isinstance(added_user, User), "Should add a User instance to the session"
#     assert added_user.username == "testuser"

#     # 2. db.session.commit should be called
#     mock_session.commit.assert_called_once()

#     # 3. The returned user object should match
#     assert created_user is added_user, "create_user should return the same user added to the session"

#     # 4. The password should be hashed (not the same as raw text)
#     #    We'll verify the hashed password with check_password_hash
#     assert check_password_hash(created_user.password_hash, "testpass"), \
#         "Password should be hashed and match the provided password"


# @patch("app.services.User")  # We'll patch the User model in app.services
# def test_check_existing_user_found(mock_user_class):
#     """
#     Tests that check_existing_user returns a user if found.
#     """
#     # Arrange
#     mock_user = MagicMock()
#     mock_user.username = "existinguser"

#     # Mock the query so filter_by(...) returns an object whose first() is our mock_user
#     mock_query = MagicMock()
#     mock_query.first.return_value = mock_user
#     mock_user_class.query.filter_by.return_value = mock_query

#     # Act
#     found_user = check_existing_user("existinguser")

#     # Assert
#     mock_user_class.query.filter_by.assert_called_once_with(username="existinguser")
#     mock_query.first.assert_called_once()
#     assert found_user is mock_user, "Should return the user if found"


# @patch("app.services.User")
# def test_check_existing_user_not_found(mock_user_class):
#     """
#     Tests that check_existing_user returns None if no user is found.
#     """
#     # Arrange
#     mock_query = MagicMock()
#     mock_query.first.return_value = None
#     mock_user_class.query.filter_by.return_value = mock_query

#     # Act
#     found_user = check_existing_user("non_existent")

#     # Assert
#     mock_user_class.query.filter_by.assert_called_once_with(username="non_existent")
#     mock_query.first.assert_called_once()
#     assert found_user is None, "Should return None if user not found"
