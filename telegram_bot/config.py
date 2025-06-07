import os

from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class Config:
    TOKEN: str = os.getenv('TOKEN')
    API_URL: str = os.getenv('API_URL')
