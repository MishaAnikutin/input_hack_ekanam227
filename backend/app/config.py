import dotenv
import os

dotenv.load_dotenv()


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    ALLOWS_ORIGINS = os.getenv("ALLOWS_ORIGINS")
    ALLOWS_METHODS = os.getenv("ALLOWS_METHODS")
    ALLOWS_HEADERS = os.getenv("ALLOWS_HEADERS")

    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_KEY = os.getenv("QDRANT_KEY")

    OPENAI_URL = os.getenv("OPENAI_URL")
    OPENAI_KEY = os.getenv("OPENAI_KEY")
