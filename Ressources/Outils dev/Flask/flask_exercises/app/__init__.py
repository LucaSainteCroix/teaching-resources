from flask import Flask
from flask_login import LoginManager
# from config import Config
# from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import config_manager
from app.database import DatabaseManager


# Load extensions
login_manager = LoginManager()
db_manager = DatabaseManager()

csrf = CSRFProtect()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_manager[config_name])

    csrf.init_app(app)
    login_manager.init_app(app)
    db_manager.init_app(app)

    migrate = Migrate(app, db_manager)

    from app.routes import register_routes
    register_routes(app)

    # db = SQLAlchemy(app)

    return app
