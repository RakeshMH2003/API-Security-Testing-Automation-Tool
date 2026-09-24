import sys
import os
import traceback

api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

try:
    from app.main import app
except Exception as e:
    # If import fails, create a dummy FastAPI app to return the error
    from fastapi import FastAPI
    app = FastAPI()
    
    error_msg = traceback.format_exc()
    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def catch_all(path: str):
        return {"error": "Initialization failed", "traceback": error_msg}
