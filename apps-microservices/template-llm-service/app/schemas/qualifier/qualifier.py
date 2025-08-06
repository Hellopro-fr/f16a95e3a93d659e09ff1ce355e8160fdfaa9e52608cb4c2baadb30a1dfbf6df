# Schéma d'entrée pour la qualification
from pydantic import BaseModel
from typing import Optional, Dict, Any

class QualifyRequest(BaseModel):
    url: str

class QualifyResponse(BaseModel):
    type_page: str
    chunk: Optional[str]
    metadata: Optional[Dict[str, Any]]
