from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from pathlib import Path
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = Path(__file__).parent / 'upload'
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['SECRET_KEY'] = 'you-will-never-guess'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login = LoginManager(app)

from main import views
from main import models
