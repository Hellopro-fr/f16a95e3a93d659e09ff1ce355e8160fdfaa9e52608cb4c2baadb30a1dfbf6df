from fastapi import APIRouter, HTTPException, Depends
from app.schemas.qualifier.qualifier import QualifyRequest, QualifyResponse
from app.core.qualifier.service import QualifierService
from typing import Annotated

router = APIRouter()

# Le système de lazy loading reste le même, il est toujours aussi pertinent.
qualifier_service_instance: QualifierService | None = None

def get_qualifier_service() -> QualifierService:
    global qualifier_service_instance
    if qualifier_service_instance is None:
        print("--- LAZY LOADING: Initialisation du QualifierService (chargement du modèle)... ---")
        qualifier_service_instance = QualifierService()
        print("--- LAZY LOADING: Service initialisé et prêt. ---")
    return qualifier_service_instance

@router.post("/", response_model=QualifyResponse)
async def qualify(
    request: QualifyRequest, # Le modèle de requête a changé
    service: Annotated[QualifierService, Depends(get_qualifier_service)]
):
    # On appelle le service avec les deux arguments
    type_page, chunk, metadata = service.classify(url=request.url, content=request.content)
    
    # La vérification de contenu non trouvé n'est plus nécessaire ici
    # car le contenu est toujours fourni.
    return QualifyResponse(type_page=type_page, chunk=chunk, metadata=metadata)