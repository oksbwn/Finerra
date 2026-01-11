from sqlalchemy import create_engine, text
from backend.app.core.config import settings
import sys

# Ensure backend directory is in path for imports to work if running as script
import os
sys.path.append(os.getcwd())

def test_connection():
    try:
        print(f"Connecting to: {settings.DATABASE_URL}")
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            print(f"Connection successful! Result: {result}")
            return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
