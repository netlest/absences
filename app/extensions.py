from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_session import Session

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
session = Session()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
