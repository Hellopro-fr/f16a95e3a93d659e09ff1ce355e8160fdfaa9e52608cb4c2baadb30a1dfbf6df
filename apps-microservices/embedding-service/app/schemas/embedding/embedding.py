from pydantic import BaseModel
from typing import List, Dict, Any

class EmbedRequest(BaseModel):
    texte_brute: str
    id_unique: str
    type_page: str = "autre"

class EmbedResponse(BaseModel):
    data: List[Dict[str, Any]]