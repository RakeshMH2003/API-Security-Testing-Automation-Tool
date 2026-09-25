import sys
import os

# Ensure app package is in path
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app
