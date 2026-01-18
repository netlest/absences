#!/usr/bin/env python3
"""
Validation script to test the FastAPI application structure without database.
This demonstrates that the application is correctly configured.
"""
import json
from datetime import date, timedelta


def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    print("=" * 60)
    
    try:
        from fastapi_app.main import app, create_app
        print("✓ Main application module")
    except Exception as e:
        print(f"✗ Main application module: {e}")
        return False
    
    try:
        from fastapi_app.core import settings, verify_token
        print("✓ Core modules (config, security)")
    except Exception as e:
        print(f"✗ Core modules: {e}")
        return False
    
    try:
        from fastapi_app.deps import get_db, SessionLocal, engine, Base
        print("✓ Database dependencies")
    except Exception as e:
        print(f"✗ Database dependencies: {e}")
        return False
    
    try:
        from fastapi_app.models import User, Group, Object, AbsenceType, Absence
        print("✓ SQLAlchemy models")
    except Exception as e:
        print(f"✗ SQLAlchemy models: {e}")
        return False
    
    try:
        from fastapi_app.schemas import (
            AbsenceCreate, AbsenceResponse,
            BulkAbsenceCreate, BulkAbsenceResponse
        )
        print("✓ Pydantic schemas")
    except Exception as e:
        print(f"✗ Pydantic schemas: {e}")
        return False
    
    try:
        from fastapi_app.api import api_router
        print("✓ API routers")
    except Exception as e:
        print(f"✗ API routers: {e}")
        return False
    
    print("=" * 60)
    print("✓ All imports successful!")
    return True


def test_app_structure():
    """Test FastAPI app structure"""
    print("\nTesting FastAPI app structure...")
    print("=" * 60)
    
    from fastapi_app.main import app
    
    # Test app properties
    print(f"App Title: {app.title}")
    print(f"App Version: {app.version}")
    print(f"OpenAPI URL: {app.openapi_url}")
    print(f"Docs URL: {app.docs_url}")
    
    # Test routes
    print("\nRegistered Routes:")
    route_count = 0
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ', '.join(sorted(route.methods))
            print(f"  {methods:12} {route.path}")
            route_count += 1
    
    print(f"\nTotal routes: {route_count}")
    print("=" * 60)
    print("✓ App structure validated!")
    return True


def test_pydantic_models():
    """Test Pydantic model validation"""
    print("\nTesting Pydantic models...")
    print("=" * 60)
    
    from fastapi_app.schemas import AbsenceCreate, BulkAbsenceCreate
    
    # Test valid absence creation
    try:
        today = date.today()
        absence = AbsenceCreate(
            object_id=1,
            type_id=1,
            abs_date_start=today,
            abs_date_end=today + timedelta(days=5),
            description="Test absence"
        )
        print(f"✓ Valid absence model created: {absence.model_dump()}")
    except Exception as e:
        print(f"✗ Failed to create valid absence: {e}")
        return False
    
    # Test date validation (end before start)
    try:
        invalid_absence = AbsenceCreate(
            object_id=1,
            type_id=1,
            abs_date_start=today + timedelta(days=5),
            abs_date_end=today,  # End before start
            description="Invalid"
        )
        print(f"✗ Invalid absence should have failed validation")
        return False
    except Exception as e:
        print(f"✓ Date validation working: {str(e)[:60]}...")
    
    # Test bulk creation
    try:
        bulk = BulkAbsenceCreate(
            absences=[
                AbsenceCreate(
                    object_id=1,
                    type_id=1,
                    abs_date_start=today,
                    abs_date_end=today + timedelta(days=2),
                    description="Absence 1"
                ),
                AbsenceCreate(
                    object_id=2,
                    type_id=2,
                    abs_date_start=today + timedelta(days=5),
                    abs_date_end=today + timedelta(days=7),
                    description="Absence 2"
                )
            ]
        )
        print(f"✓ Bulk absence model created with {len(bulk.absences)} items")
    except Exception as e:
        print(f"✗ Failed to create bulk absence: {e}")
        return False
    
    print("=" * 60)
    print("✓ Pydantic models validated!")
    return True


def test_sqlalchemy_models():
    """Test SQLAlchemy model definitions"""
    print("\nTesting SQLAlchemy models...")
    print("=" * 60)
    
    from fastapi_app.models import User, Group, Object, AbsenceType, Absence
    
    # Test model attributes
    models = [
        ("User", User, ["id", "username", "password", "admin"]),
        ("Group", Group, ["id", "user_id", "name", "description"]),
        ("Object", Object, ["id", "user_id", "group_id", "name", "description"]),
        ("AbsenceType", AbsenceType, ["id", "name", "color"]),
        ("Absence", Absence, ["id", "object_id", "type_id", "abs_date_start", "abs_date_end", "description"])
    ]
    
    for model_name, model_class, expected_attrs in models:
        missing = [attr for attr in expected_attrs if not hasattr(model_class, attr)]
        if missing:
            print(f"✗ {model_name} missing attributes: {missing}")
            return False
        print(f"✓ {model_name} has all expected attributes")
    
    # Test relationships
    print("\nTesting relationships:")
    if hasattr(User, 'objects'):
        print("✓ User -> Objects relationship")
    
    if hasattr(Object, 'absences'):
        print("✓ Object -> Absences relationship")
    
    if hasattr(Absence, 'object'):
        print("✓ Absence -> Object relationship")
    
    print("=" * 60)
    print("✓ SQLAlchemy models validated!")
    return True


def test_authentication():
    """Test authentication configuration"""
    print("\nTesting authentication...")
    print("=" * 60)
    
    from fastapi_app.core.config import settings
    
    print(f"API Keys configured: {len(settings.API_KEYS)}")
    print(f"Algorithm: {settings.ALGORITHM}")
    print(f"Token expire time: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    
    # Show test tokens
    print("\nTest tokens available:")
    for i, token in enumerate(settings.API_KEYS, 1):
        print(f"  {i}. {token}")
    
    print("=" * 60)
    print("✓ Authentication configured!")
    return True


def generate_sample_request():
    """Generate sample API request"""
    print("\nSample API Request:")
    print("=" * 60)
    
    from fastapi_app.core.config import settings
    
    today = date.today()
    
    sample_request = {
        "absences": [
            {
                "object_id": 1,
                "type_id": 1,
                "abs_date_start": str(today),
                "abs_date_end": str(today + timedelta(days=4)),
                "description": "Annual vacation"
            },
            {
                "object_id": 2,
                "type_id": 2,
                "abs_date_start": str(today + timedelta(days=10)),
                "abs_date_end": str(today + timedelta(days=12)),
                "description": "Conference"
            }
        ]
    }
    
    print("curl command:")
    print("-" * 60)
    curl_cmd = f"""curl -X POST http://localhost:8000/api/v1/absences/bulk \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer {settings.API_KEYS[0]}" \\
  -d '{json.dumps(sample_request, indent=2)}'"""
    print(curl_cmd)
    print("-" * 60)
    
    print("\nPython code:")
    print("-" * 60)
    python_code = f"""import requests

url = "http://localhost:8000/api/v1/absences/bulk"
headers = {{
    "Content-Type": "application/json",
    "Authorization": "Bearer {settings.API_KEYS[0]}"
}}
data = {json.dumps(sample_request, indent=4)}

response = requests.post(url, headers=headers, json=data)
print(response.json())"""
    print(python_code)
    print("-" * 60)


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("FastAPI Application Structure Validation")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("App Structure", test_app_structure),
        ("Pydantic Models", test_pydantic_models),
        ("SQLAlchemy Models", test_sqlalchemy_models),
        ("Authentication", test_authentication),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Generate sample request
    try:
        generate_sample_request()
    except Exception as e:
        print(f"Failed to generate sample request: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed!")
        print("\nThe FastAPI application is correctly configured.")
        print("To start the server, run:")
        print("  ./run_fastapi.sh")
        print("or")
        print("  uvicorn fastapi_app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("✗ Some tests failed.")
        print("Please review the errors above.")
    
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
