# FastAPI Integration with Best Practices

This repository now includes a complete **FastAPI application** demonstrating best practices for:

- **SQLAlchemy 2.0** with mapped models
- **Pydantic v2** for validation
- **Bearer token authentication**
- **Bulk insert operations**
- **PostgreSQL** integration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create or update your `.env` file:

```env
DB_USER=postgres
DB_PASS=your_password
DB_HOST=localhost
DB_NAME=absences
SECRET_KEY=your-secret-key-here
```

### 3. Start the FastAPI Server

```bash
# Using the startup script
./run_fastapi.sh

# Or directly with uvicorn
uvicorn fastapi_app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc

## What's Included

### Project Structure

```
fastapi_app/
├── __init__.py
├── main.py                    # FastAPI application entry point
├── README.md                  # Detailed documentation
├── example_usage.py           # Example Python client
├── api/
│   ├── __init__.py
│   └── absences.py           # API endpoints
├── core/
│   ├── config.py             # Configuration management
│   └── security.py           # Authentication logic
├── deps/
│   └── database.py           # Database session management
├── models/
│   └── models.py             # SQLAlchemy mapped models
└── schemas/
    └── absences.py           # Pydantic validation schemas
```

### Key Features

#### 1. **SQLAlchemy 2.0 Mapped Models**

Using modern `mapped_column` with type hints:

```python
class Absence(Base):
    __tablename__ = "absences"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    object_id: Mapped[int] = mapped_column(ForeignKey("objects.id"))
    abs_date_start: Mapped[date] = mapped_column(Date, nullable=False)
    abs_date_end: Mapped[date] = mapped_column(Date, nullable=False)
```

#### 2. **Pydantic Models for Validation**

Request validation with business logic:

```python
class AbsenceCreate(BaseModel):
    object_id: int = Field(..., gt=0)
    type_id: int = Field(..., gt=0)
    abs_date_start: date
    abs_date_end: date
    
    @field_validator('abs_date_end')
    def validate_date_range(cls, v, info):
        if v < info.data['abs_date_start']:
            raise ValueError('End date must be >= start date')
        return v
```

#### 3. **Bearer Token Authentication**

Simple yet effective token-based auth:

```python
@router.post("/absences/bulk")
async def bulk_create(
    data: BulkAbsenceCreate,
    token: str = Depends(verify_token),  # Authentication
    db: Session = Depends(get_db),       # Database session
):
    # Implementation
```

#### 4. **Bulk Insert Endpoint**

Efficient batch insertion with validation:

```python
POST /api/v1/absences/bulk
{
  "absences": [
    {
      "object_id": 1,
      "type_id": 1,
      "abs_date_start": "2024-01-01",
      "abs_date_end": "2024-01-05",
      "description": "Vacation"
    }
  ]
}
```

## Usage Examples

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Bulk insert with authentication
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
curl -H "Authorization: Bearer demo-api-key-12345" \
  http://localhost:8000/api/v1/absences/
```

### Using Python

```python
import requests

API_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "Authorization": "Bearer demo-api-key-12345",
    "Content-Type": "application/json"
}

# Bulk insert
data = {
    "absences": [
        {
            "object_id": 1,
            "type_id": 1,
            "abs_date_start": "2024-01-01",
            "abs_date_end": "2024-01-05",
            "description": "Vacation"
        }
    ]
}

response = requests.post(
    f"{API_URL}/absences/bulk",
    headers=HEADERS,
    json=data
)
print(response.json())
```

### Using the Example Script

```bash
# Run the example usage script
python fastapi_app/example_usage.py
```

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Health check | No |
| GET | `/` | Root endpoint | No |
| POST | `/api/v1/absences/bulk` | Bulk insert absences | Yes |
| POST | `/api/v1/absences/` | Create single absence | Yes |
| GET | `/api/v1/absences/` | List absences | Yes |
| GET | `/api/v1/absences/{id}` | Get specific absence | Yes |

## Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer your-token-here
```

**Default test tokens** (for development):
- `demo-api-key-12345`
- `test-bearer-token-67890`

**⚠️ Production Note**: Replace with proper JWT authentication in production.

## Best Practices Demonstrated

### 1. **Configuration Management**
- Using `pydantic-settings` for environment variables
- Single source of truth for configuration
- Type-safe settings

### 2. **Database Session Management**
- Dependency injection with `Depends(get_db)`
- Automatic session cleanup
- Connection pooling

### 3. **Transaction Management**
- Atomic operations
- Automatic rollback on errors
- Commit only on success

### 4. **Error Handling**
- Comprehensive exception handling
- Meaningful error messages
- Proper HTTP status codes

### 5. **Input Validation**
- Pydantic models for type checking
- Custom validators for business logic
- Foreign key validation before insertion

### 6. **Code Organization**
- Clean separation of concerns
- Modular structure
- Clear imports and exports

### 7. **Documentation**
- OpenAPI/Swagger automatic documentation
- Docstrings for all functions
- README with examples

## Testing the API

### 1. Interactive Documentation

Open http://localhost:8000/docs in your browser to:
- Explore all endpoints
- Test API calls directly
- See request/response schemas
- Try authentication

### 2. Example Script

Run the included example:

```bash
python fastapi_app/example_usage.py
```

### 3. Manual Testing

Use curl, Postman, or any HTTP client with the endpoints listed above.

## Integration with Flask App

The FastAPI application is **separate** from the existing Flask application:

- **Flask app** (existing): Web UI for absence management
- **FastAPI app** (new): REST API for programmatic access
- **Shared database**: Both connect to the same PostgreSQL database

You can:
1. Run both applications simultaneously on different ports
2. Use FastAPI for API clients and Flask for web interface
3. Gradually migrate to FastAPI if desired

## Performance Considerations

- ✅ Connection pooling (10 connections + 20 overflow)
- ✅ Bulk insert using `add_all()`
- ✅ Pre-validation of foreign keys
- ✅ Efficient query patterns
- ✅ Proper indexes on database (existing)

## Security Considerations

### Current Implementation
- Simple API key authentication (for demonstration)
- Input validation via Pydantic
- SQL injection prevention via ORM
- Proper error handling

### Production Recommendations
1. Implement JWT authentication
2. Store tokens in database with hashing
3. Add rate limiting
4. Use HTTPS only
5. Implement refresh tokens
6. Add request logging
7. Set up monitoring

## Troubleshooting

### API won't start

```bash
# Check if required packages are installed
pip install -r requirements.txt

# Verify database connection
python -c "from fastapi_app.deps import engine; engine.connect()"
```

### Authentication errors

- Verify you're using the correct token
- Check the `Authorization` header format: `Bearer <token>`
- Default tokens are in `fastapi_app/core/config.py`

### Database errors

- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Verify tables exist (run Flask migrations if needed)

## Further Reading

- Detailed documentation: `fastapi_app/README.md`
- FastAPI docs: https://fastapi.tiangolo.com/
- SQLAlchemy 2.0 docs: https://docs.sqlalchemy.org/
- Pydantic docs: https://docs.pydantic.dev/

## Support

For questions or issues, please create an issue in the repository.
