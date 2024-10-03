import os
import pickle
from credentials import db_password

db_credentials = pickle.load(open( "db_credentials.p", "rb" ))

db_password = db_credentials['password']
db_username = db_credentials['username']
db_server_address = 'localhost'
db_port = '3306'
db_name = 'flask_example'

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ma_cle_aleatoire'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'app.db')
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'mysql://{db_username}:{db_password}@{db_server_address}:{db_port}/{db_name}'