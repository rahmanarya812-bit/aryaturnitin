import uvicorn
import os
import sys

if __name__ == "__main__":
    # Ensure current directory is in sys.path
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    sys.path.insert(0, backend_dir)
    
    print("==================================================")
    print("  TURNITIN CLONE ENGINE SERVER STARTING")
    print("  URL Dashboard : http://localhost:8000")
    print("  API Docs      : http://localhost:8000/docs")
    print("==================================================")

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
