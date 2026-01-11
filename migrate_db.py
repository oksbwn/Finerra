from sqlalchemy import text
from backend.app.core.database import engine

def run_migration():
    print("Running migration: Adding account_mask column to accounts table...")
    with engine.connect() as conn:
        try:
            # DuckDB/PostgreSQL syntax for adding a column
            # IF NOT EXISTS is not standard SQL92 in ALTER TABLE, but DuckDB supports basic ALTER
            # We wrap in try/except to handle "Duplicate column" if run twice
            conn.execute(text("ALTER TABLE accounts ADD COLUMN account_mask VARCHAR"))
            print("Success: Column 'account_mask' added.")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("Notice: Column 'account_mask' already exists. Skipping.")
            else:
                print(f"Error: {e}")
                raise e

if __name__ == "__main__":
    run_migration()
