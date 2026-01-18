"""
Security utilities for authentication and authorization.
Best practice: Centralize security logic for reusability.
"""
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

# Best practice: Use FastAPI's security utilities
security = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """
    Verify bearer token.
    Best practice: Use dependency injection for authentication.
    
    In production, you would:
    1. Decode JWT tokens
    2. Verify token signature
    3. Check token expiration
    4. Load user from database
    
    For this example, we use simple API key verification.
    """
    token = credentials.credentials
    
    if token not in settings.API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


# Example of JWT token creation (commented out as we use simple API keys)
# from datetime import datetime, timedelta
# from jose import JWTError, jwt
# 
# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     """Create JWT access token"""
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt
