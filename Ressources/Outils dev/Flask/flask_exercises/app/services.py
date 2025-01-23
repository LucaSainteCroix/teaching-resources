# app/services.py
from app import db_manager as db
from app.models import User
import bcrypt

def create_user(form):

    hash = bcrypt.hashpw(form.password.data.encode(), bcrypt.gensalt())
    password_hash = hash.decode()

    user = User(username=form.username.data,
                email=form.email.data,
                password_hash=password_hash)

    db.session.add(user)
    db.session.commit()

    return user

def check_existing_user(username):
    user = User.query.filter_by(username=username).first()
    return user
