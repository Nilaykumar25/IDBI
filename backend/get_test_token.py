"""
Helper script to create a test user and get a valid JWT token for API testing
"""
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    exit(1)

# Test user credentials
TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "TestPassword123!"

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("Attempting to sign in with test user...")
    
    # Try to sign in first
    try:
        response = supabase.auth.sign_in_with_password({
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        print("✓ Successfully signed in with existing test user")
    except Exception as signin_error:
        print(f"Sign in failed: {signin_error}")
        print("Attempting to create new test user...")
        
        # If sign in fails, try to create the user
        try:
            response = supabase.auth.sign_up({
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
            print("✓ Successfully created new test user")
            
            # After signup, sign in to get a fresh token
            response = supabase.auth.sign_in_with_password({
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            })
        except Exception as signup_error:
            print(f"✗ Failed to create test user: {signup_error}")
            exit(1)
    
    # Extract access token
    if response.session and response.session.access_token:
        token = response.session.access_token
        print()
        print("=" * 80)
        print("JWT ACCESS TOKEN (valid for API testing):")
        print("=" * 80)
        print(token)
        print("=" * 80)
        print()
        print("Copy this token and use it in your API tests:")
        print(f'  Authorization: Bearer {token}')
        print()
        
        # Save to file for easy access
        with open('test_token.txt', 'w') as f:
            f.write(token)
        print("✓ Token saved to test_token.txt")
        
    else:
        print("✗ No session token received")
        exit(1)
        
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)
