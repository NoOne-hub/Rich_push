from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_basicauth import BasicAuth

app = Flask(__name__)
basic_auth = BasicAuth(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
sche = BackgroundScheduler()
sche.start()
from app import routes
