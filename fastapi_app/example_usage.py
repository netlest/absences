#!/usr/bin/env python3
"""
Example script demonstrating how to use the FastAPI bulk insert endpoint.
This script shows best practices for interacting with the API.
"""
import json
import requests
from datetime import date, timedelta
from typing import List, Dict, Any


class AbsencesAPIClient:
    """
    Client for interacting with the Absences API.
    Best practice: Create reusable API client classes.
    """
    
    def __init__(self, base_url: str, api_token: str):
        """Initialize API client with base URL and authentication token"""
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def bulk_create_absences(self, absences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk create absences.
        
        Args:
            absences: List of absence dictionaries
            
        Returns:
            API response with created absences
        """
        payload = {"absences": absences}
        response = requests.post(
            f"{self.base_url}/api/v1/absences/bulk",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def create_absence(self, absence: Dict[str, Any]) -> Dict[str, Any]:
        """Create a single absence"""
        response = requests.post(
            f"{self.base_url}/api/v1/absences/",
            headers=self.headers,
            json=absence
        )
        response.raise_for_status()
        return response.json()
    
    def list_absences(
        self,
        skip: int = 0,
        limit: int = 100,
        object_id: int = None
    ) -> List[Dict[str, Any]]:
        """List absences with optional filtering"""
        params = {"skip": skip, "limit": limit}
        if object_id:
            params["object_id"] = object_id
        
        response = requests.get(
            f"{self.base_url}/api/v1/absences/",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_absence(self, absence_id: int) -> Dict[str, Any]:
        """Get a specific absence by ID"""
        response = requests.get(
            f"{self.base_url}/api/v1/absences/{absence_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()


def example_bulk_insert():
    """
    Example demonstrating bulk insert functionality.
    Best practice: Clear, documented examples.
    """
    # Initialize API client
    client = AbsencesAPIClient(
        base_url="http://localhost:8000",
        api_token="demo-api-key-12345"
    )
    
    print("=" * 60)
    print("FastAPI Bulk Insert Example")
    print("=" * 60)
    
    # Check API health
    print("\n1. Checking API health...")
    try:
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Database: {health['database']}")
    except Exception as e:
        print(f"   Error: {e}")
        print("   Make sure the API is running: uvicorn fastapi_app.main:app")
        return
    
    # Example 1: Bulk insert multiple absences
    print("\n2. Bulk inserting absences...")
    
    today = date.today()
    absences_to_create = [
        {
            "object_id": 1,
            "type_id": 1,
            "abs_date_start": str(today),
            "abs_date_end": str(today + timedelta(days=4)),
            "description": "Annual vacation"
        },
        {
            "object_id": 1,
            "type_id": 2,
            "abs_date_start": str(today + timedelta(days=10)),
            "abs_date_end": str(today + timedelta(days=12)),
            "description": "Conference attendance"
        },
        {
            "object_id": 2,
            "type_id": 1,
            "abs_date_start": str(today + timedelta(days=5)),
            "abs_date_end": str(today + timedelta(days=7)),
            "description": "Personal leave"
        }
    ]
    
    try:
        result = client.bulk_create_absences(absences_to_create)
        print(f"   Created {result['created_count']} absences")
        print(f"   Absence IDs: {[a['id'] for a in result['absences']]}")
    except requests.exceptions.HTTPError as e:
        print(f"   Error: {e.response.status_code}")
        print(f"   Detail: {e.response.json().get('detail')}")
        print("\n   Note: Make sure objects with IDs 1,2 and absence types with IDs 1,2 exist in the database.")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Example 2: List absences
    print("\n3. Listing absences...")
    try:
        absences = client.list_absences(limit=5)
        print(f"   Found {len(absences)} absences")
        for absence in absences[:3]:  # Show first 3
            print(f"   - ID: {absence['id']}, Object: {absence['object_id']}, "
                  f"Dates: {absence['abs_date_start']} to {absence['abs_date_end']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open http://localhost:8000/docs for interactive API documentation")
    print("2. Try different API endpoints using the Swagger UI")
    print("3. Modify this script to test your specific use cases")


def example_error_handling():
    """
    Example demonstrating error handling.
    Best practice: Always handle potential errors.
    """
    client = AbsencesAPIClient(
        base_url="http://localhost:8000",
        api_token="demo-api-key-12345"
    )
    
    print("\n" + "=" * 60)
    print("Error Handling Examples")
    print("=" * 60)
    
    # Example: Invalid token
    print("\n1. Testing invalid token...")
    invalid_client = AbsencesAPIClient(
        base_url="http://localhost:8000",
        api_token="invalid-token"
    )
    
    try:
        invalid_client.list_absences()
    except requests.exceptions.HTTPError as e:
        print(f"   Expected error: {e.response.status_code} - {e.response.json()['detail']}")
    
    # Example: Invalid date range
    print("\n2. Testing invalid date range...")
    try:
        invalid_absence = {
            "object_id": 1,
            "type_id": 1,
            "abs_date_start": "2024-01-10",
            "abs_date_end": "2024-01-05",  # End before start
            "description": "Invalid"
        }
        client.create_absence(invalid_absence)
    except requests.exceptions.HTTPError as e:
        print(f"   Expected error: {e.response.status_code}")
        error_detail = e.response.json()
        print(f"   Detail: {error_detail}")
    
    # Example: Non-existent object
    print("\n3. Testing non-existent object...")
    try:
        invalid_absence = {
            "object_id": 99999,  # Likely doesn't exist
            "type_id": 1,
            "abs_date_start": "2024-01-01",
            "abs_date_end": "2024-01-05",
            "description": "Test"
        }
        client.create_absence(invalid_absence)
    except requests.exceptions.HTTPError as e:
        print(f"   Expected error: {e.response.status_code} - {e.response.json()['detail']}")


if __name__ == "__main__":
    print("\nFastAPI + SQLAlchemy Best Practices Demo")
    print("=" * 60)
    
    # Run the main example
    example_bulk_insert()
    
    # Run error handling examples
    example_error_handling()
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
