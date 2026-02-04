from sqlalchemy import text
from sqlalchemy.engine import Engine

def run_auto_migrations(engine: Engine):
    """
    Runs auto-migration logic to ensure the parser database schema matches the models.
    """
    try:
        with engine.connect() as connection:
            print("Running Parser Service migrations...")
            
            # Helper to add columns safely
            def safe_add_column(table, col, type_def):
                try:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {type_def}"))
                except Exception as e:
                    print(f"DEBUG: safe_add_column potential issue: {e}")

            # 1. Create merchant_aliases table if not exists
            connection.execute(text("""
            CREATE TABLE IF NOT EXISTS merchant_aliases (
                id VARCHAR PRIMARY KEY,
                pattern VARCHAR NOT NULL UNIQUE,
                alias VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """))
            
            # 2. Update pattern_rules with AI fields
            safe_add_column("pattern_rules", "is_ai_generated", "BOOLEAN DEFAULT FALSE")
            safe_add_column("pattern_rules", "confidence", "JSON")

            # Explicitly commit if needed (DuckDB depends on connection mode)
            connection.commit()
            print("Parser Service migrations complete.")
            
    except Exception as e:
        print(f"CRITICAL: Parser migration failed: {e}")
        raise e
