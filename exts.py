from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_cors import CORS
from flask_pymongo import PyMongo

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
cors = CORS()
mongo = PyMongo()
