import pytest
from unittest.mock import patch, MagicMock
# from app import create_app, db_manager
from app.models import User  # Import your models
from app.services import create_user, check_existing_user
import bcrypt



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
    # """
    # By using @pytest.mark.usefixtures("test_app"),
    # each test method in this class will have access to the test_app fixture.
    # """

    # def test_create_user(app):
    #     # Arrange: A mock registration form
    #     form = MockForm(username="testuser", email="test@example.com", password="secret123")

    #     # Act: We call create_user
    #     user = create_user(form)

    #     # Assert: A User should be added to the database
    #     assert user.id is not None, "User should have an ID after creation"
    #     assert user.username == "testuser"
    #     assert user.email == "test@example.com"
    #     assert user.password_hash != "secret123"  # password is hashed

    # def test_check_existing_user(app, db):
    #     # Arrange: A user already in the DB
    #         # created by the existing_user fixture
    #     hash = bcrypt.hashpw("secret123".encode(), bcrypt.gensalt())
    #     password_hash = hash.decode()
    #     new_user = User(username="testuser", email="test@example.com", password_hash=password_hash)

    #     db.session.add(new_user)
    #     db.session.commit()
    #     # Act: We check for that user
    #     found_user = check_existing_user("testuser")

    #     # Assert: We should get the user object back
    #     assert found_user is not None
    #     assert found_user.username == "test_user"

    def test_check_non_existent_user(app):
        # Act: We look for a user that doesn't exist
        found_user = check_existing_user("ghost")

        # Assert: We should get None
        assert found_user is None






# @pytest.fixture(scope='session')
# def test_app():
#     """Create a Flask test application with a new db instance."""
#     # Create a new Flask app instance for testing
#     app = Flask(__name__)
#     app.config.from_object(TestConfig)

#     # Initialize extensions with the test app
#     db = SQLAlchemy(app)
#     migrate = Migrate(app, db)
#     login = LoginManager(app)
#     csrf = CSRFProtect(app)

#     # Import models to ensure they're registered with SQLAlchemy
#     from app import models

#     return app

# @pytest.fixture(scope='session')
# def test_db(test_app):
#     """Create test database tables."""
#     from app import db
#     with test_app.app_context():
#         db.create_all()
#         yield db
#         db.drop_all()

# @pytest.fixture(scope='function')
# def session(test_db, test_app):
#     """Create a fresh database session for each test."""
#     connection = test_db.engine.connect()
#     transaction = connection.begin()

#     # Begin a nested transaction
#     options = dict(bind=connection, binds={})
#     session = test_db.create_scoped_session(options=options)

#     test_db.session = session

#     yield session

#     # Rollback the transaction
#     session.close()
#     transaction.rollback()
#     connection.close()

# @pytest.fixture
# def test_form():
#     """Create a test form with user data."""
#     class TestForm:
#         class Username:
#             data = "testuser"
#         class Password:
#             data = "testpass"
#         username = Username()
#         password = Password()
#     return TestForm()

# class TestUserServicesIntegration:
#     def test_create_user_integration(session, test_app, test_form):
#         """Test creating a user in the database"""
#         with test_app.app_context():
#             from app.services import create_user

#             # Act
#             user = create_user(test_form)

#             # Assert
#             assert user.id is not None
#             assert user.username == "testuser"

#             # Verify user exists in database
#             db_user = User.query.filter_by(username="testuser").first()
#             assert db_user is not None
#             assert db_user.id == user.id

#     def test_check_existing_user_integration(session, test_app, test_form):
#         """Test checking for existing users in the database"""
#         with test_app.app_context():
#         # Arrange
#             user = create_user(test_form)

#             # Act
#             existing_user = check_existing_user("testuser")
#             non_existing_user = check_existing_user("nonexistent")

#             # Assert
#             assert existing_user is not None
#             assert existing_user.id == user.id
#             assert non_existing_user is None

#     def test_duplicate_username(self, session, test_form):
#         """Test handling of duplicate usernames"""
#         with test_app.app_context():
#             # Arrange
#             create_user(test_form)

#             # Act & Assert
#             with pytest.raises(Exception):  # Adjust exception type based on your error handling
#                 create_user(test_form)

# # You can keep your existing unit tests unchanged
# class TestUserServicesUnit:
#     @pytest.fixture
#     def mock_form(self):
#         form = MagicMock()
#         form.username.data = "testuser"
#         form.password.data = "testpass"
#         return form

#     # ... rest of your unit tests ...
