"""
Main FastAPI application.
Best practice: Clean application factory pattern with proper configuration.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from .core.config import settings
from .api import api_router
from .schemas import HealthCheckResponse
from .deps import get_db


def create_app() -> FastAPI:
    """
    Application factory.
    Best practice: Use factory pattern for application creation.
    """
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="""
        Absences API with best practices for FastAPI and SQLAlchemy.
        
        ## Features
        - SQLAlchemy 2.0 with mapped_column
        - Pydantic v2 models for validation
        - Bearer token authentication
        - Bulk insert endpoint
        - Proper error handling
        - Transaction management
        - Connection pooling
        - API documentation
        
        ## Authentication
        Use Bearer token authentication by including the header:
        ```
        Authorization: Bearer your-token-here
        ```
        
        Default tokens for testing:
        - demo-api-key-12345
        - test-bearer-token-67890
        """,
        openapi_tags=[
            {
                "name": "absences",
                "description": "Operations with absences",
            },
            {
                "name": "health",
                "description": "Health check endpoints",
            },
        ],
    )
    
    # Best practice: Configure CORS if needed
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify actual origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Best practice: Global exception handler for database errors
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Database error occurred"}
        )
    
    # Best practice: Include routers with versioned prefix
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    
    # Best practice: Health check endpoint
    @app.get(
        "/health",
        response_model=HealthCheckResponse,
        tags=["health"],
        summary="Health check",
        description="Check if the API and database are operational"
    )
    async def health_check():
        """Health check endpoint"""
        db_status = "ok"
        try:
            # Test database connection
            db = next(get_db())
            db.execute("SELECT 1")
            db.close()
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return HealthCheckResponse(
            status="ok" if db_status == "ok" else "degraded",
            database=db_status
        )
    
    @app.get("/", tags=["health"])
    async def root():
        """Root endpoint"""
        return {
            "message": "Absences API",
            "docs": "/docs",
            "health": "/health"
        }
    
    return app


# Create application instance
# Best practice: Create app instance that can be used by ASGI servers
app = create_app()


if __name__ == "__main__":
    # Best practice: Allow running with uvicorn directly
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload in development
        log_level="info"
    )
