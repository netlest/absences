# gunicorn_config.py
from dotenv import load_dotenv
load_dotenv()
bind = "0.0.0.0:8000"
workers = 4
