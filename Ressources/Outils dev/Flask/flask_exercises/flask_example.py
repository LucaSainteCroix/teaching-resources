import os
from dotenv import load_dotenv, find_dotenv

import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, db_manager
from app.models import User, Post



_ = load_dotenv(find_dotenv())

app = create_app(os.getenv("FLASK_CONFIG") or "dev")


@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db_manager, 'User': User, 'Post': Post}
