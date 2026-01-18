"""
FastAPI Application Package
Best practice: Clean package structure with clear exports.
"""
from .main import app, create_app

__all__ = ["app", "create_app"]
