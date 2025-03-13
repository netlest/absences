import os
import logging

from dotenv import load_dotenv
from flask import Flask
from config import config
from sqlalchemy.exc import OperationalError

from .extensions import db, migrate, login_manager, csrf, session
from .blueprints import auth, main, user, sitemap, month, object, group, debug, types, manage, holiday, abs
from .cli import init_cli
from . import errors

load_dotenv()

def create_app():
    app = Flask(__name__)
    env = os.getenv('FLASK_ENV', 'production')
    config_class = config.get(env, config['production'])
    app.config.from_object(config_class)
    app.config['ROOT_PATH'] = app.root_path
    app.config['INSTANCE_PATH'] = app.instance_path
    app.config['SESSION_SQLALCHEMY'] = db

    # Create instance directory if it doesn't exist
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # Create log directory if it doesn't exist
    log_dir = os.path.join(app.instance_path, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create migrations directory if it doesn't exist
    migrations_dir = os.path.join(app.instance_path, 'migrations')
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir)

    
    # Initialize extensions
    # Session will fail if the database is not created
    try:
        db.init_app(app)
        session.init_app(app)
    except OperationalError as e:
        pass
    
    # csrf.init_app(app)
    migrate.init_app(app, db, directory=migrations_dir)
    login_manager.init_app(app)

    # Configure logger
    formatter = logging.Formatter(f'%(asctime)s %(levelname)s %(name)s : %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(os.path.join(log_dir, f'{__name__}.log'))
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)


    # Register blueprints
    app.register_blueprint(errors.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(debug.bp)
    app.register_blueprint(sitemap.bp)
    app.register_blueprint(month.bp)
    app.register_blueprint(object.bp)
    app.register_blueprint(group.bp)
    app.register_blueprint(manage.bp)
    app.register_blueprint(types.bp)
    app.register_blueprint(holiday.bp)
    app.register_blueprint(abs.bp)

    # Register CLI commands
    init_cli(app)

    if env == 'development':
        # Log all configuration items
        for key, value in app.config.items():
            app.logger.info(f"{key}: {value}")

    return app
