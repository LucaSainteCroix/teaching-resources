# Third-party imports
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import event
from sqlalchemy import create_engine
import bcrypt
import pytest

# App imports
from app import create_app, db_manager as db
from app.models import Base, User, Post


@pytest.fixture(scope="session", autouse=True)
def app_context(request):

    app = create_app(config_name="test")

       # Create application context
    with app.app_context():
        # Create all database tables
        db.base.metadata.create_all(db.engine)
        yield app
        # Clean up after all tests
        db.session.remove()
        db.base.metadata.drop_all(db.engine)


@pytest.fixture(scope='function')
def db_session():
    """Provide a clean database session for each test.

    This fixture runs for each test function, creating a fresh database
    transaction that can be rolled back after the test completes."""

    # Start a transaction
    connection = db.engine.connect()
    transaction = connection.begin()

    # Use a nested transaction for tests
    db.session.begin_nested()

    yield db.session

    # Roll back the transaction after each test
    db.session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture()
def user_details():
    class UserDetails(object):
        test_username = "test_user"
        test_email = "test@email.com"
        test_password = "my_secure_password"

    return UserDetails


@pytest.fixture()
def existing_user(db_session, user_details):

    hash = bcrypt.hashpw(user_details.test_password.encode(), bcrypt.gensalt())
    password_hash = hash.decode()

    user_model = User(
        username=user_details.test_username,
        password_hash=password_hash,
        email=user_details.test_email
    )
    db_session.add(user_model)
    db_session.commit()
    return user_model



@pytest.fixture()
def post_details():
    class PostDetails(object):
        test_body = "this is a test post"
        test_user_id = 1

    return PostDetails


@pytest.fixture()
def existing_post(db_session, post_details):


    post_model = Post(
        body=post_details.test_body,
        user_id=post_details.test_user_id,
    )
    db_session.session.add(post_model)
    db_session.session.commit()
    return post_model
