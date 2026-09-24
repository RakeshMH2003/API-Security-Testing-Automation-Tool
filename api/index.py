import sys
import os

api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

from app.main import app

# Create a variable named app for Vercel Serverless Function to find
app = app
