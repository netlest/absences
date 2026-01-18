#!/usr/bin/env python3
"""
Utility script to generate JWT tokens for testing the FastAPI application.
This helps users quickly create tokens without writing code.
"""
import sys
import os
from datetime import timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi_app.auth import create_access_token


def generate_token(username: str, expires_minutes: int = 30) -> str:
    """
    Generate a JWT token for a given username.
    
    Args:
        username: Username to encode in the token
        expires_minutes: Token expiration time in minutes
        
    Returns:
        str: JWT token
    """
    token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=expires_minutes)
    )
    return token


def main():
    """Main function to generate token from command line."""
    if len(sys.argv) < 2:
        print("Usage: python generate_token.py <username> [expires_minutes]")
        print("\nExample:")
        print("  python generate_token.py admin 60")
        print("\nThis will generate a token for user 'admin' that expires in 60 minutes.")
        sys.exit(1)
    
    username = sys.argv[1]
    expires_minutes = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    token = generate_token(username, expires_minutes)
    
    print(f"\n{'='*70}")
    print(f"JWT Token generated for user: {username}")
    print(f"Expires in: {expires_minutes} minutes")
    print(f"{'='*70}\n")
    print(f"Token:\n{token}\n")
    print(f"{'='*70}")
    print(f"\nUse this token in your requests:")
    print(f"\ncurl -X POST 'http://localhost:8000/api/v1/absences/bulk' \\")
    print(f"  -H 'Authorization: Bearer {token}' \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{{\"absences\": [...]}}'\n")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
