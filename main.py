"""
OpenTradeJournal-AI: Main Application Entrypoint
Launches the FastAPI server via Uvicorn.
"""

import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

def main():
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"==================================================")
    print(f"🚀 Launching OpenTradeJournal-AI Server on {host}:{port}")
    print(f"Documentation available at: http://localhost:{port}/docs")
    print(f"==================================================")
    
    uvicorn.run("src.api.server:app", host=host, port=port, reload=debug)

if __name__ == "__main__":
    main()
