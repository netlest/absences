"""
Main FastAPI application entry point.
Demonstrates best practices for FastAPI application structure.
"""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .routes import router as absences_router
from .database import engine, Base

# Application metadata
APP_TITLE = "Absences Management API"
APP_DESCRIPTION = """
FastAPI application for managing absences with best practices.

## Features

* **Bearer Token Authentication**: Secure API endpoints with JWT tokens
* **SQLAlchemy 2.0**: Modern ORM with async support and mapped models
* **Pydantic Validation**: Automatic request/response validation
* **Bulk Operations**: Efficient bulk insert endpoint
* **PostgreSQL**: Production-ready database support
* **Async/Await**: Full async support for high performance

## Authentication

All endpoints require authentication using Bearer token in the Authorization header:

```
Authorization: Bearer <your-token-here>
```

## Bulk Insert

The bulk insert endpoint (`POST /api/v1/absences/bulk`) accepts a JSON list of absence dictionaries:

```json
{
  "absences": [
    {
      "object_id": 1,
      "type_id": 1,
      "abs_date_start": "2024-01-01",
      "abs_date_end": "2024-01-05",
      "description": "Vacation"
    },
    {
      "object_id": 2,
      "type_id": 2,
      "abs_date_start": "2024-01-10",
      "abs_date_end": "2024-01-12",
      "description": "Sick leave"
    }
  ]
}
```
"""
APP_VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    
    This is the modern way to handle startup/shutdown events in FastAPI.
    """
    # Startup: Create database tables if they don't exist
    # Note: In production, use Alembic migrations instead
    async with engine.begin() as conn:
        # Uncomment the following line to create tables on startup
        # await conn.run_sync(Base.metadata.create_all)
        pass
    
    yield
    
    # Shutdown: Clean up resources
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register routers
app.include_router(absences_router)


# Root endpoint
@app.get(
    "/",
    tags=["root"],
    summary="API root",
    description="Get API information and status"
)
async def root():
    """Root endpoint providing API information."""
    return {
        "name": APP_TITLE,
        "version": APP_VERSION,
        "status": "operational",
        "docs": "/api/docs",
        "redoc": "/api/redoc",
    }


# Health check endpoint
@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Check if the API is healthy and operational"
)
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": APP_VERSION,
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error": str(exc)
        }
    )
