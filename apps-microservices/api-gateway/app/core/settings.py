from dataclasses import dataclass
import os
from typing import Dict, Type
from dotenv import load_dotenv

from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


@dataclass(frozen=True)
class Service:
    """Represents a microservice with its URL and the API path to access it."""
    url: str
    api_path: str

class Configuration:
    PROJECT_NAME: str = "API-HP-RAG"
    PROJECT_VERSION: str = "0.0.1"

    CLEANER: Service = Service(
        url=str(os.getenv("CLEANER", "http://localhost:8001")), 
        api_path="/cleaner-service"
    )
    SCRAPING: Service = Service(
        url=str(os.getenv("SCRAPING", "http://localhost:8002")), 
        api_path="/scraping-service"
    )
    EMBEDDING: Service = Service(
        url=str(os.getenv("EMBEDDING", "http://localhost:8003")), 
        api_path="/embedding-service"
    )

    DOCUMENT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def _create_service_map(config_class: Type[Configuration]) -> Dict[str, str]:
    """
    Inspects the Configuration class and automatically builds the SERVICE_MAP.
    It finds all attributes of type 'Service' and maps their api_path to their url.
    """
    service_map = {}
    # Iterate over all attributes of the Configuration class
    for attr_name, attr_value in vars(config_class).items():
        # If the attribute is an instance of our Service class, add it to the map
        if isinstance(attr_value, Service):
            service_map[attr_value.api_path] = attr_value.url
    return service_map

SERVICE_MAP = _create_service_map(Configuration)
settings = Configuration()