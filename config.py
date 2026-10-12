import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
DATABASE_URL = os.getenv("DATABASE_URL")