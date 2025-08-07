import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

class Config:
    ZILLIZ_URI: Optional[str] = os.getenv("ZILLIZ_URI")
    ZILLIZ_API_KEY: Optional[str] = os.getenv("ZILLIZ_API_KEY")
    RECREATE_COLLECTIONS: bool = False