import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Configuration:
    PROJECT_NAME: str = "API-HP-RAG"
    PROJECT_VERSION: str = "0.0.1"

    CLEANER: str = f"{os.getenv("CLEANER")}"
    SCRAPING: str = f"{os.getenv("SCRAPING")}"
    DOCUMENT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


settings = Configuration()