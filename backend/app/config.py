import dotenv
import os

dotenv.load_dotenv()


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    ALLOWS_ORIGINS = os.getenv("ALLOWS_ORIGINS")
    ALLOWS_METHODS = os.getenv("ALLOWS_METHODS")
    ALLOWS_HEADERS = os.getenv("ALLOWS_HEADERS")

    QDRANT_HOST = os.getenv("QDRANT_HOST")
    QDRANT_PORT = os.getenv("QDRANT_PORT")

