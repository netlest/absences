import os

class Config:
    DB_USER = os.environ.get('DB_USER')
    DB_PASS = os.environ.get('DB_PASS')
    DB_HOST = os.environ.get('DB_HOST')
    DB_NAME = os.environ.get('DB_NAME')
    DB_ADMIN_USER = os.environ.get('DB_ADMIN_USER')
    DB_ADMIN_PASS = os.environ.get('DB_ADMIN_PASS')
    SECRET_KEY = os.getenv('SECRET_KEY', 'neverguessthis')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = "sqlalchemy"
    SESSION_PERMANENT = True
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
    USE_SESSION_FOR_NEXT = True
    SHOW_ALL_GROUP_OBJECTS = True       # Whether or not to show all objects in the group or just the user's objects
    MODIFY_ALL_GROUP_ABSENCES = False   # Whether or not to allow the user to modify all group absences or just their own object absences
    
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
   
class ProductionConfig(Config):
    # SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    pass

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

