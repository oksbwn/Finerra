import uvicorn
import os
import sys

# Ensure the current directory (project root) is in sys.path
sys.path.append(os.getcwd())

if __name__ == "__main__":
    # Run Uvicorn programmatically
    # This avoids "python -m uvicorn" CLI parsing issues and ensures paths are set
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
