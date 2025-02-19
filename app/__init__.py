from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_ldap3_login import LDAP3LoginManager
from flask_login import LoginManager, login_user, UserMixin, current_user

app = Flask(__name__, static_folder="static")
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# initialize LDAP manager
login_manager = LoginManager(app)  # setup a Flask-login manager
login_manager.login_view = 'login'
ldap_manager = LDAP3LoginManager(app)  # Setup a LDAP3 Login Manager
ldap_manager.init_app(app)

from app import routes, models, forms