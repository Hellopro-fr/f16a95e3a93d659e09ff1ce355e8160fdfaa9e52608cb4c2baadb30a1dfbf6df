from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class QualifyRequest(BaseModel):
    url: str
    content: str = Field(..., description="Le contenu HTML ou texte de la page à classifier.")

class QualifyResponse(BaseModel):
    type_page: str
    chunk: Optional[str]
    metadata: Optional[Dict[str, Any]]