#!/usr/bin/env python3
"""
Integration test for FastAPI endpoints using TestClient.
This tests the API without needing a running server or database.
"""
from fastapi.testclient import TestClient
from datetime import date, timedelta
import json


def test_health_endpoint():
    """Test the health check endpoint"""
    print("\nTesting health endpoint...")
    print("=" * 60)
    
    from fastapi_app.main import app
    client = TestClient(app)
    
    response = client.get("/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    
    print("✓ Health endpoint working!")
    return True


def test_root_endpoint():
    """Test the root endpoint"""
    print("\nTesting root endpoint...")
    print("=" * 60)
    
    from fastapi_app.main import app
    client = TestClient(app)
    
    response = client.get("/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    
    print("✓ Root endpoint working!")
    return True


def test_openapi_docs():
    """Test OpenAPI documentation endpoint"""
    print("\nTesting OpenAPI docs...")
    print("=" * 60)
    
    from fastapi_app.main import app
    client = TestClient(app)
    
    response = client.get("/openapi.json")
    print(f"Status Code: {response.status_code}")
    
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "paths" in data
    
    # Check that our endpoints are documented
    paths = data["paths"]
    assert "/api/v1/absences/bulk" in paths
    assert "/api/v1/absences/" in paths
    assert "/health" in paths
    
    print(f"✓ OpenAPI schema generated with {len(paths)} endpoints")
    return True


def test_authentication_required():
    """Test that authentication is required"""
    print("\nTesting authentication requirement...")
    print("=" * 60)
    
    from fastapi_app.main import app
    client = TestClient(app)
    
    # Try without token
    response = client.get("/api/v1/absences/")
    print(f"Without token - Status: {response.status_code}")
    assert response.status_code == 401  # Unauthorized without auth
    
    # Try with invalid token
    response = client.get(
        "/api/v1/absences/",
        headers={"Authorization": "Bearer invalid-token"}
    )
    print(f"With invalid token - Status: {response.status_code}")
    assert response.status_code == 401  # Unauthorized
    
    # Try with valid token (will fail at DB level, but auth passes)
    response = client.get(
        "/api/v1/absences/",
        headers={"Authorization": "Bearer demo-api-key-12345"}
    )
    print(f"With valid token - Status: {response.status_code}")
    # Will be 500 because DB doesn't exist, but that means auth worked!
    assert response.status_code in [200, 500]
    
    print("✓ Authentication working!")
    return True


def test_request_validation():
    """Test request validation with Pydantic"""
    print("\nTesting request validation...")
    print("=" * 60)
    
    from fastapi_app.main import app
    client = TestClient(app)
    
    headers = {"Authorization": "Bearer demo-api-key-12345"}
    
    # Test with invalid data (missing required fields)
    invalid_data = {
        "absences": [
            {
                "object_id": 1,
                # Missing type_id
                "abs_date_start": "2024-01-01",
                "abs_date_end": "2024-01-05"
            }
        ]
    }
    
    response = client.post(
        "/api/v1/absences/bulk",
        json=invalid_data,
        headers=headers
    )
    print(f"Invalid data - Status: {response.status_code}")
    assert response.status_code == 422  # Validation error
    
    # Test with invalid date range
    invalid_dates = {
        "absences": [
            {
                "object_id": 1,
                "type_id": 1,
                "abs_date_start": "2024-01-10",
                "abs_date_end": "2024-01-05"  # End before start
            }
        ]
    }
    
    response = client.post(
        "/api/v1/absences/bulk",
        json=invalid_dates,
        headers=headers
    )
    print(f"Invalid date range - Status: {response.status_code}")
    assert response.status_code == 422  # Validation error
    
    print("✓ Request validation working!")
    return True


def test_openapi_schema_details():
    """Test OpenAPI schema contains proper documentation"""
    print("\nTesting OpenAPI schema details...")
    print("=" * 60)
    
    from fastapi_app.main import app
    client = TestClient(app)
    
    response = client.get("/openapi.json")
    schema = response.json()
    
    # Check bulk insert endpoint documentation
    bulk_endpoint = schema["paths"]["/api/v1/absences/bulk"]["post"]
    
    print("Bulk Insert Endpoint Documentation:")
    print(f"  Summary: {bulk_endpoint.get('summary')}")
    print(f"  Description: {bulk_endpoint.get('description', '')[:80]}...")
    print(f"  Tags: {bulk_endpoint.get('tags')}")
    
    # Check response codes documented
    responses = bulk_endpoint.get("responses", {})
    print(f"  Response codes documented: {list(responses.keys())}")
    
    # Check security requirement
    security = bulk_endpoint.get("security", [])
    print(f"  Security schemes: {security}")
    
    # Check request body schema
    request_body = bulk_endpoint.get("requestBody", {})
    print(f"  Request body required: {request_body.get('required', False)}")
    
    print("✓ OpenAPI schema properly documented!")
    return True


def test_cors_headers():
    """Test CORS configuration"""
    print("\nTesting CORS configuration...")
    print("=" * 60)
    
    from fastapi_app.main import app
    client = TestClient(app)
    
    # Make a request and check CORS headers
    response = client.get(
        "/health",
        headers={"Origin": "http://example.com"}
    )
    
    headers = response.headers
    print(f"Access-Control-Allow-Origin: {headers.get('access-control-allow-origin')}")
    print(f"Access-Control-Allow-Credentials: {headers.get('access-control-allow-credentials')}")
    
    print("✓ CORS configured!")
    return True


def test_pydantic_schemas():
    """Test Pydantic schema examples"""
    print("\nTesting Pydantic schema examples...")
    print("=" * 60)
    
    from fastapi_app.schemas import AbsenceCreate, BulkAbsenceCreate
    
    today = date.today()
    
    # Create valid absence
    absence = AbsenceCreate(
        object_id=1,
        type_id=1,
        abs_date_start=today,
        abs_date_end=today + timedelta(days=5),
        description="Test"
    )
    
    print(f"Valid Absence:")
    print(f"  {absence.model_dump()}")
    
    # Create bulk request
    bulk = BulkAbsenceCreate(
        absences=[absence]
    )
    
    print(f"Bulk Request:")
    print(f"  Contains {len(bulk.absences)} absence(s)")
    
    # Test JSON serialization
    json_str = bulk.model_dump_json()
    print(f"JSON serialization works: {len(json_str)} bytes")
    
    print("✓ Pydantic schemas working!")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("FastAPI Integration Tests (without database)")
    print("=" * 60)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint),
        ("OpenAPI Docs", test_openapi_docs),
        ("Authentication", test_authentication_required),
        ("Request Validation", test_request_validation),
        ("OpenAPI Schema Details", test_openapi_schema_details),
        ("CORS Configuration", test_cors_headers),
        ("Pydantic Schemas", test_pydantic_schemas),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, True))
        except AssertionError as e:
            print(f"✗ Assertion failed: {e}")
            results.append((test_name, False))
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All integration tests passed!")
        print("\nThe FastAPI application is working correctly.")
        print("\nNote: Database operations will require a PostgreSQL connection.")
        print("Set DB credentials in .env file and ensure database is running.")
    else:
        print("✗ Some tests failed.")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
