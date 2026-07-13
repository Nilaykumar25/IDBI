"""
Basic setup verification script.
Tests that the backend can start and configuration is valid.
"""
import sys
import os

def test_imports():
    """Test that all required packages are installed."""
    print("Testing imports...")
    try:
        import flask
        print(f"  ✓ Flask {flask.__version__}")
    except ImportError:
        print("  ✗ Flask not found")
        return False
    
    try:
        import flask_cors
        print("  ✓ Flask-CORS installed")
    except ImportError:
        print("  ✗ Flask-CORS not found")
        return False
    
    try:
        import supabase
        print("  ✓ Supabase client installed")
    except ImportError:
        print("  ✗ Supabase client not found")
        return False
    
    try:
        import dotenv
        print("  ✓ python-dotenv installed")
    except ImportError:
        print("  ✗ python-dotenv not found")
        return False
    
    return True

def test_config():
    """Test that configuration can be loaded."""
    print("\nTesting configuration...")
    try:
        from config import Config
        print("  ✓ Config module loaded")
        
        # Check if .env exists
        if os.path.exists('.env'):
            print("  ✓ .env file exists")
        else:
            print("  ⚠ .env file not found (using defaults)")
        
        # Try to load config values
        if Config.SUPABASE_URL and Config.SUPABASE_KEY:
            print("  ✓ Supabase configuration present")
        else:
            print("  ⚠ Supabase configuration incomplete")
            print("    → Edit .env with your Supabase credentials")
        
        print(f"  ✓ Adapter mode: {Config.ADAPTER_MODE}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error loading config: {e}")
        return False

def test_app_creation():
    """Test that Flask app can be created."""
    print("\nTesting Flask app creation...")
    try:
        from app import create_app
        app = create_app()
        print("  ✓ Flask app created successfully")
        print(f"  ✓ Debug mode: {app.config['DEBUG']}")
        print(f"  ✓ Adapter mode: {app.config['ADAPTER_MODE']}")
        return True
    except Exception as e:
        print(f"  ✗ Error creating Flask app: {e}")
        return False

def test_middleware():
    """Test that auth middleware can be imported."""
    print("\nTesting middleware...")
    try:
        from middleware.auth import require_auth
        print("  ✓ Auth middleware loaded")
        return True
    except Exception as e:
        print(f"  ✗ Error loading middleware: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("MSME Financial Health Score - Setup Verification")
    print("=" * 50)
    
    results = []
    
    results.append(test_imports())
    results.append(test_config())
    results.append(test_app_creation())
    results.append(test_middleware())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✓ All tests passed!")
        print("=" * 50)
        print("\nBackend setup is complete.")
        print("\nNext steps:")
        print("1. Configure .env with Supabase credentials (if not done)")
        print("2. Start the backend: python app.py")
        print("3. Set up the frontend (see README.md)")
        return 0
    else:
        print("✗ Some tests failed")
        print("=" * 50)
        print("\nPlease fix the issues above and try again.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
