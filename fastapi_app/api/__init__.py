"""API module - router aggregation"""
from fastapi import APIRouter
from .absences import router as absences_router

# Best practice: Aggregate all routers in a single API router
api_router = APIRouter()
api_router.include_router(absences_router)

__all__ = ["api_router"]
