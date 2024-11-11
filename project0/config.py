
import os
import secrets

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY') or secrets.token_hex(32)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')