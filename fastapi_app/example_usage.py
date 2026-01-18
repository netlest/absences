#!/usr/bin/env python3
"""
Example script demonstrating FastAPI application usage.
Shows how to generate tokens and make API requests.
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict

# Test configuration
TEST_USERNAME = "testuser"
API_BASE_URL = "http://localhost:8000"

# Example data for bulk insert
EXAMPLE_ABSENCES = [
    {
        "object_id": 1,
        "type_id": 1,
        "abs_date_start": "2024-01-01",
        "abs_date_end": "2024-01-05",
        "description": "New Year Vacation"
    },
    {
        "object_id": 1,
        "type_id": 2,
        "abs_date_start": "2024-02-10",
        "abs_date_end": "2024-02-12",
        "description": "Sick Leave"
    },
    {
        "object_id": 2,
        "type_id": 1,
        "abs_date_start": "2024-03-15",
        "abs_date_end": "2024-03-22",
        "description": "Spring Holiday"
    },
]


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f" {title}")
    print(f"{'='*70}\n")


def generate_example_token() -> str:
    """Generate a test token."""
    import sys
    import os
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from fastapi_app.auth import create_access_token
    
    token = create_access_token(
        data={"sub": TEST_USERNAME},
        expires_delta=timedelta(minutes=60)
    )
    return token


def print_curl_examples(token: str):
    """Print curl command examples."""
    print_section("cURL Examples")
    
    print("1. Check API health:")
    print(f"   curl -s {API_BASE_URL}/health | python3 -m json.tool\n")
    
    print("2. Get API information:")
    print(f"   curl -s {API_BASE_URL}/ | python3 -m json.tool\n")
    
    print("3. Bulk create absences:")
    print(f"   curl -X POST '{API_BASE_URL}/api/v1/absences/bulk' \\")
    print(f"     -H 'Authorization: Bearer {token}' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d @fastapi_app/example_bulk_insert.json | python3 -m json.tool\n")
    
    print("4. Create a single absence:")
    print(f"   curl -X POST '{API_BASE_URL}/api/v1/absences/' \\")
    print(f"     -H 'Authorization: Bearer {token}' \\")
    print(f"     -H 'Content-Type: application/json' \\")
    print(f"     -d '{{\"object_id\": 1, \"type_id\": 1, \"abs_date_start\": \"2024-01-01\", \"abs_date_end\": \"2024-01-05\"}}' | python3 -m json.tool\n")
    
    print("5. List all absences:")
    print(f"   curl -s -H 'Authorization: Bearer {token}' \\")
    print(f"     '{API_BASE_URL}/api/v1/absences/' | python3 -m json.tool\n")
    
    print("6. Get a specific absence:")
    print(f"   curl -s -H 'Authorization: Bearer {token}' \\")
    print(f"     '{API_BASE_URL}/api/v1/absences/1' | python3 -m json.tool\n")
    
    print("7. Delete an absence:")
    print(f"   curl -X DELETE -s -H 'Authorization: Bearer {token}' \\")
    print(f"     '{API_BASE_URL}/api/v1/absences/1' | python3 -m json.tool\n")


def print_python_examples(token: str):
    """Print Python request examples."""
    print_section("Python requests Examples")
    
    print("First, install requests: pip install requests\n")
    print("```python")
    print("import requests")
    print("import json\n")
    print(f"API_URL = '{API_BASE_URL}'")
    print(f"TOKEN = '{token}'\n")
    print("headers = {")
    print("    'Authorization': f'Bearer {TOKEN}',")
    print("    'Content-Type': 'application/json'")
    print("}\n")
    
    print("# 1. Health check")
    print("response = requests.get(f'{API_URL}/health')")
    print("print(response.json())\n")
    
    print("# 2. Bulk create absences")
    print("bulk_data = {")
    print("    'absences': [")
    print("        {")
    print("            'object_id': 1,")
    print("            'type_id': 1,")
    print("            'abs_date_start': '2024-01-01',")
    print("            'abs_date_end': '2024-01-05',")
    print("            'description': 'Vacation'")
    print("        }")
    print("    ]")
    print("}")
    print("response = requests.post(")
    print("    f'{API_URL}/api/v1/absences/bulk',")
    print("    headers=headers,")
    print("    json=bulk_data")
    print(")")
    print("print(response.json())\n")
    
    print("# 3. List absences")
    print("response = requests.get(")
    print("    f'{API_URL}/api/v1/absences/',")
    print("    headers=headers")
    print(")")
    print("print(response.json())")
    print("```\n")


def print_best_practices():
    """Print best practices summary."""
    print_section("Best Practices Implemented")
    
    practices = [
        "1. SQLAlchemy 2.0 Mapped Models",
        "   - Using Mapped[type] with mapped_column()",
        "   - Type hints for better IDE support",
        "   - Modern declarative syntax",
        "",
        "2. Pydantic Models",
        "   - Request/response validation",
        "   - Custom validators for business logic",
        "   - Automatic OpenAPI documentation",
        "",
        "3. Bearer Token Authentication",
        "   - JWT tokens with expiration",
        "   - Secure password hashing with bcrypt",
        "   - Dependency injection for auth",
        "",
        "4. Async/Await",
        "   - Full async database operations",
        "   - AsyncSession for database",
        "   - Proper session management",
        "",
        "5. Bulk Operations",
        "   - Transaction management (all or nothing)",
        "   - Validation before insert",
        "   - Efficient batch processing",
        "",
        "6. Error Handling",
        "   - Proper HTTP status codes",
        "   - Automatic rollback on errors",
        "   - Descriptive error messages",
        "",
        "7. API Documentation",
        "   - Auto-generated OpenAPI schema",
        "   - Interactive Swagger UI",
        "   - ReDoc alternative view",
        "",
        "8. Database Best Practices",
        "   - Connection pooling",
        "   - Dependency injection for sessions",
        "   - Proper relationship loading",
    ]
    
    for practice in practices:
        print(practice)


def main():
    """Main function."""
    print_section("FastAPI Absences Management API - Usage Examples")
    
    print("This script demonstrates how to use the FastAPI application.")
    print("Make sure the server is running before trying these examples.\n")
    print("Start the server with:")
    print("  uvicorn fastapi_app.main:app --reload --port 8000\n")
    
    # Generate token
    try:
        token = generate_example_token()
        print_section("Generated Test Token")
        print(f"Token: {token}")
        print(f"\nThis token is valid for 60 minutes.")
        print(f"Use it in the Authorization header as: Bearer {token}")
        
        # Print examples
        print_curl_examples(token)
        print_python_examples(token)
        print_best_practices()
        
        print_section("Next Steps")
        print("1. Access API documentation at: http://localhost:8000/api/docs")
        print("2. Try the interactive API at: http://localhost:8000/api/redoc")
        print("3. Use the examples above to test the endpoints")
        print("4. Review the code in fastapi_app/ directory for implementation details\n")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have installed all dependencies:")
        print("  pip install -r requirements.txt")


if __name__ == "__main__":
    main()
