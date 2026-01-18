# FastAPI with SQLAlchemy Best Practices

This is a demonstration of **best practices** for building a FastAPI application with SQLAlchemy, featuring:

- ✅ SQLAlchemy 2.0 with `mapped_column` and modern type hints
- ✅ Pydantic v2 models for request/response validation
- ✅ Bearer token authentication
- ✅ Bulk insert endpoint for efficient data insertion
- ✅ Proper database session management with dependency injection
- ✅ Transaction management (all-or-nothing operations)
- ✅ Connection pooling
- ✅ Comprehensive error handling
- ✅ API documentation with OpenAPI/Swagger

## Project Structure

```
fastapi_app/
├── __init__.py
├── main.py                 # FastAPI application factory
├── api/
│   ├── __init__.py
│   └── absences.py        # Absence endpoints with bulk insert
├── core/
│   ├── __init__.py
│   ├── config.py          # Configuration with pydantic-settings
│   └── security.py        # Authentication logic
├── deps/
│   ├── __init__.py
│   └── database.py        # Database session management
├── models/
│   ├── __init__.py
│   └── models.py          # SQLAlchemy models (mapped_column)
└── schemas/
    ├── __init__.py
    └── absences.py        # Pydantic schemas
```

## Best Practices Demonstrated

### 1. SQLAlchemy 2.0 Style with Mapped Models

Using modern `mapped_column` with type hints for better IDE support:

```python
from sqlalchemy.orm import Mapped, mapped_column

class Absence(Base):
    __tablename__ = "absences"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    object_id: Mapped[int] = mapped_column(ForeignKey("objects.id"))
    abs_date_start: Mapped[date] = mapped_column(Date, nullable=False)
```

### 2. Pydantic Models for Validation

Separate schemas for input validation and output serialization:

```python
class AbsenceCreate(BaseModel):
    object_id: int = Field(..., gt=0)
    type_id: int = Field(..., gt=0)
    abs_date_start: date
    abs_date_end: date
    
    @field_validator('abs_date_end')
    @classmethod
    def validate_date_range(cls, v: date, info) -> date:
        if v < info.data['abs_date_start']:
            raise ValueError('End date must be >= start date')
        return v
```

### 3. Dependency Injection

Using FastAPI's dependency injection for database sessions and authentication:

```python
async def bulk_create_absences(
    bulk_data: BulkAbsenceCreate,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token),
):
    # Function body
```

### 4. Transaction Management

Atomic operations with proper rollback on errors:

```python
try:
    db.add_all(absence_objects)
    db.commit()
except Exception:
    db.rollback()
    raise
```

### 5. Connection Pooling

Configured engine with connection pool:

```python
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)
```

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables (create `.env` file):

```env
DB_USER=postgres
DB_PASS=your_password
DB_HOST=localhost
DB_NAME=absences
SECRET_KEY=your-secret-key-here
```

## Running the Application

### Development Mode

```bash
# Using uvicorn directly
uvicorn fastapi_app.main:app --reload --host 0.0.0.0 --port 8000

# Or run the main file
python -m fastapi_app.main
```

### Production Mode

```bash
# Using gunicorn with uvicorn workers
gunicorn fastapi_app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Authentication

All endpoints require Bearer token authentication. Include the token in the header:

```bash
Authorization: Bearer demo-api-key-12345
```

Default test tokens:
- `demo-api-key-12345`
- `test-bearer-token-67890`

### Health Check

```bash
GET /health
```

### Bulk Insert Absences

```bash
POST /api/v1/absences/bulk
Content-Type: application/json
Authorization: Bearer demo-api-key-12345

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

### Create Single Absence

```bash
POST /api/v1/absences/
Content-Type: application/json
Authorization: Bearer demo-api-key-12345

{
  "object_id": 1,
  "type_id": 1,
  "abs_date_start": "2024-01-01",
  "abs_date_end": "2024-01-05",
  "description": "Vacation"
}
```

### List Absences

```bash
GET /api/v1/absences/?skip=0&limit=100&object_id=1
Authorization: Bearer demo-api-key-12345
```

### Get Single Absence

```bash
GET /api/v1/absences/1
Authorization: Bearer demo-api-key-12345
```

## Example Usage with curl

```bash
# Health check
curl http://localhost:8000/health

# Bulk insert
curl -X POST http://localhost:8000/api/v1/absences/bulk \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer demo-api-key-12345" \
  -d '{
    "absences": [
      {
        "object_id": 1,
        "type_id": 1,
        "abs_date_start": "2024-01-01",
        "abs_date_end": "2024-01-05",
        "description": "Vacation"
      }
    ]
  }'

# List absences
curl http://localhost:8000/api/v1/absences/ \
  -H "Authorization: Bearer demo-api-key-12345"
```

## Example Usage with Python

```python
import requests
import json

API_URL = "http://localhost:8000/api/v1"
TOKEN = "demo-api-key-12345"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Bulk insert absences
absences_data = {
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

response = requests.post(
    f"{API_URL}/absences/bulk",
    headers=HEADERS,
    json=absences_data
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# List absences
response = requests.get(
    f"{API_URL}/absences/",
    headers=HEADERS
)
print(f"Absences: {response.json()}")
```

## Database Schema

The FastAPI application uses the existing database schema:

- **users**: User accounts
- **groups**: Organizational groups
- **objects**: Entities that can have absences
- **absence_types**: Types/categories of absences
- **absences**: Absence records

## Security Considerations

### Current Implementation (for demonstration)

- Simple API key validation
- Keys stored in configuration

### Production Recommendations

1. **Use JWT tokens** instead of static API keys
2. **Store tokens in database** with proper hashing
3. **Implement token expiration** and refresh mechanism
4. **Use HTTPS** in production
5. **Rate limiting** to prevent abuse
6. **Input sanitization** (Pydantic handles this)
7. **SQL injection prevention** (SQLAlchemy ORM handles this)

## Performance Optimizations

1. **Bulk Insert**: Uses `db.add_all()` for efficient batch insertion
2. **Connection Pooling**: Reuses database connections
3. **Lazy Loading**: Relationships loaded on-demand
4. **Index Usage**: Relies on database indexes on foreign keys
5. **Query Optimization**: Validates foreign keys with single queries

## Error Handling

The API provides detailed error responses:

- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: Resource doesn't exist
- `500 Internal Server Error`: Server-side errors

Example error response:

```json
{
  "detail": "Objects not found: {999}",
  "status_code": 404
}
```

## Testing

You can test the API using:

1. **Swagger UI**: http://localhost:8000/docs
2. **ReDoc**: http://localhost:8000/redoc
3. **curl** (see examples above)
4. **Python requests** (see examples above)
5. **Postman** or similar API clients

## Integration with Existing Flask App

This FastAPI application is **separate** from the existing Flask application:

- **Flask app**: Handles web UI (runs on its own port)
- **FastAPI app**: Handles API endpoints (runs on its own port)
- **Shared database**: Both apps connect to the same PostgreSQL database

You can run both applications simultaneously or deploy them separately.

## Future Enhancements

1. Add JWT authentication with refresh tokens
2. Add user management endpoints
3. Add filtering and sorting for list endpoints
4. Add pagination with cursor-based approach
5. Add rate limiting
6. Add caching (Redis)
7. Add async SQLAlchemy with asyncpg
8. Add comprehensive test suite
9. Add CI/CD pipeline
10. Add monitoring and logging

## License

Same as the main absences application.

## Support

For questions or issues, please refer to the main project documentation.
