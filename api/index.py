import sys
import os

# Add root directory to sys.path for serverless Vercel imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.app import app
