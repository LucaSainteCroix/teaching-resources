import os
import pickle
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())



class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'ma_cle_aleatoire'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DATABASE_URI")

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URI")


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False

config_manager = {
    "dev": DevelopmentConfig,
    "test": TestingConfig,
    "prod": ProductionConfig,
}
