# FastAPI Absences Management API

This module provides a modern REST API implementation using FastAPI with best practices for production applications.

## Features

✅ **FastAPI Framework**: High-performance async web framework  
✅ **SQLAlchemy 2.0**: Modern ORM with `mapped_column` and type hints  
✅ **Pydantic Models**: Automatic validation and serialization  
✅ **Bearer Token Authentication**: JWT-based secure authentication  
✅ **Bulk Insert**: Efficient bulk operations with transaction management  
✅ **PostgreSQL**: Production-ready database with async support  
✅ **Async/Await**: Full async support for high performance  
✅ **OpenAPI Documentation**: Auto-generated interactive API docs  

## Architecture

```
fastapi_app/
├── __init__.py          # Package initialization
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration and session management
├── models.py            # SQLAlchemy ORM models (mapped_column syntax)
├── schemas.py           # Pydantic models for validation
├── auth.py              # Bearer token authentication
└── routes.py            # API route handlers
```

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Copy `.env_example` to `.env` and configure:

```bash
# For PostgreSQL (production)
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DB_HOST=localhost
DB_NAME=absences
DB_USER=absences_user
DB_PASS=your-password

# For SQLite (development)
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### 3. Run the Server

```bash
# Development with auto-reload
uvicorn fastapi_app.main:app --reload --port 8000

# Production with multiple workers
uvicorn fastapi_app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Access API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Authentication

All API endpoints require Bearer token authentication.

### Generate a Token

First, you need to create a token for a valid user. Here's how to generate one manually:

```python
from fastapi_app.auth import create_access_token
from datetime import timedelta

# Create token for user
token = create_access_token(
    data={"sub": "username"},
    expires_delta=timedelta(minutes=30)
)
print(f"Bearer {token}")
```

### Use the Token

Include the token in the Authorization header:

```bash
curl -X POST "http://localhost:8000/api/v1/absences/bulk" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d @absences.json
```

## API Endpoints

### Bulk Insert Absences

**POST** `/api/v1/absences/bulk`

Create multiple absences in a single request.

**Request Body:**
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

**Response:**
```json
{
  "created_count": 2,
  "absences": [
    {
      "id": 1,
      "object_id": 1,
      "type_id": 1,
      "abs_date_start": "2024-01-01",
      "abs_date_end": "2024-01-05",
      "description": "Vacation"
    },
    {
      "id": 2,
      "object_id": 2,
      "type_id": 2,
      "abs_date_start": "2024-01-10",
      "abs_date_end": "2024-01-12",
      "description": "Sick leave"
    }
  ]
}
```

### Create Single Absence

**POST** `/api/v1/absences/`

Create a single absence.

**Request Body:**
```json
{
  "object_id": 1,
  "type_id": 1,
  "abs_date_start": "2024-01-01",
  "abs_date_end": "2024-01-05",
  "description": "Vacation"
}
```

### List Absences

**GET** `/api/v1/absences/`

List all absences with pagination.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100)

### Get Absence by ID

**GET** `/api/v1/absences/{absence_id}`

Retrieve a specific absence with related object and type information.

### Delete Absence

**DELETE** `/api/v1/absences/{absence_id}`

Delete a specific absence.

## Best Practices Implemented

### 1. SQLAlchemy Mapped Models

Uses modern SQLAlchemy 2.0 syntax with `Mapped` and `mapped_column`:

```python
class Absence(Base):
    __tablename__ = 'absences'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    abs_date_start: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Relationships with type hints
    object: Mapped["Object"] = relationship("Object", back_populates="absences")
```

### 2. Pydantic Models

Strong typing and automatic validation:

```python
class AbsenceCreate(BaseModel):
    object_id: int = Field(..., gt=0)
    abs_date_start: date
    abs_date_end: date
    
    @field_validator('abs_date_end')
    def end_after_start(cls, v, info):
        if v < info.data['abs_date_start']:
            raise ValueError('End date must be after start date')
        return v
```

### 3. Dependency Injection

Clean, testable code using FastAPI's dependency injection:

```python
async def create_absence(
    absence_data: AbsenceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Function body
```

### 4. Async Database Operations

Full async support for high performance:

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 5. Bearer Token Authentication

JWT-based authentication with proper security:

```python
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # ... validate and return user
```

### 6. Transaction Management

Proper error handling with automatic rollback:

```python
try:
    db.add_all(created_absences)
    await db.commit()
    return response
except Exception:
    await db.rollback()
    raise
```

### 7. Validation at Multiple Levels

- Pydantic for request validation
- Database constraints
- Business logic validation

### 8. OpenAPI Documentation

Comprehensive API documentation with examples:

```python
@router.post(
    "/bulk",
    response_model=AbsenceBulkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk create absences",
    description="Create multiple absences in a single request..."
)
```

## Testing

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8000/health

# Bulk insert (with authentication)
curl -X POST "http://localhost:8000/api/v1/absences/bulk" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "absences": [
      {
        "object_id": 1,
        "type_id": 1,
        "abs_date_start": "2024-01-01",
        "abs_date_end": "2024-01-05",
        "description": "Test"
      }
    ]
  }'
```

### Testing with httpie

```bash
# Install httpie
pip install httpie

# Bulk insert
http POST localhost:8000/api/v1/absences/bulk \
  Authorization:"Bearer YOUR_TOKEN" \
  absences:='[{"object_id": 1, "type_id": 1, "abs_date_start": "2024-01-01", "abs_date_end": "2024-01-05"}]'
```

## Production Deployment

### With Gunicorn + Uvicorn Workers

```bash
gunicorn fastapi_app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### With Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## Security Considerations

1. **Change SECRET_KEY**: Use a strong, random secret key in production
2. **HTTPS Only**: Always use HTTPS in production
3. **CORS Configuration**: Restrict allowed origins appropriately
4. **Rate Limiting**: Consider adding rate limiting middleware
5. **Input Validation**: Pydantic provides automatic validation
6. **SQL Injection**: SQLAlchemy ORM protects against SQL injection
7. **Token Expiration**: Tokens expire after 30 minutes by default

## Performance Tips

1. **Connection Pooling**: Configured automatically by SQLAlchemy
2. **Async Operations**: All database operations are async
3. **Bulk Operations**: Use bulk endpoints for multiple records
4. **Pagination**: Always use pagination for list endpoints
5. **Eager Loading**: Relationships are loaded efficiently

## Troubleshooting

### Issue: "Could not validate credentials"

**Solution**: Ensure your token is valid and not expired. Generate a new token if needed.

### Issue: "asyncpg.exceptions.CannotConnectNowError"

**Solution**: Check your database connection settings in `.env` file.

### Issue: "Object with id X not found"

**Solution**: Ensure the referenced objects and absence types exist in the database before creating absences.

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [JWT Authentication Guide](https://jwt.io/introduction)
