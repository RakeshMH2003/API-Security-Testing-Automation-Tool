import sys
import os

# Ensure the api directory is in the Python path so `app` package can be found
api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

from app.main import app
