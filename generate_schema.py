from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from backend.app.core.database import engine, Base
# Import all models to ensure they are registered with Base metadata
from backend.app.modules.auth import models as auth_models
from backend.app.modules.finance import models as finance_models
import sys
import os

# Ensure backend directory is in path
sys.path.append(os.getcwd())

def generate_schema_sql():
    output_file = os.path.join("backend", "schema.sql")
    
    with open(output_file, 'w') as f:
        f.write("-- Auto-generated schema from SQLAlchemy models\n")
        f.write("-- Dialect: DuckDB (compatible with PostgreSQL syntax mostly)\n\n")
        
        # Sort tables directly to handle dependencies if possible, 
        # or simple loop over sorted_tables
        for table in Base.metadata.sorted_tables:
            # We use postgresql dialect compilation for DuckDB as it's closest in syntax usually for DDL
            # or generic string compilation. For DuckDB specifically we can strip compilation to string.
            create_table_sql = str(CreateTable(table).compile(engine))
            
            # Clean up formatting a bit if needed (SQLAlchemy output is usually fine)
            f.write(f"{create_table_sql};\n\n")
            
    print(f"Schema dumped to {output_file}")

if __name__ == "__main__":
    generate_schema_sql()
