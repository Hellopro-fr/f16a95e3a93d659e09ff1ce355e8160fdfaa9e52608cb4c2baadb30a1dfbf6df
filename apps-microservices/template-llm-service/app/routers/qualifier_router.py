from fastapi import APIRouter, HTTPException, Depends
from app.schemas.qualifier.qualifier import QualifyRequest, QualifyResponse
from app.core.qualifier.service import QualifierService
from typing import Annotated

router = APIRouter()

# Variable globale pour garder le service en cache (singleton)
qualifier_service_instance: QualifierService | None = None

def get_qualifier_service() -> QualifierService:
    """
    Dépendance FastAPI qui charge le service (et le modèle LLM) de manière différée
    lors du premier appel, puis le met en cache pour les appels suivants.
    """
    global qualifier_service_instance
    if qualifier_service_instance is None:
        print("--- LAZY LOADING: Initialisation du QualifierService (chargement du modèle)... ---")
        qualifier_service_instance = QualifierService()
        print("--- LAZY LOADING: Service initialisé et prêt. ---")
    return qualifier_service_instance

@router.post("/", response_model=QualifyResponse)
async def qualify(
    request: QualifyRequest,
    service: Annotated[QualifierService, Depends(get_qualifier_service)]
):
    type_page, chunk, metadata = service.classify(request.url)
    if type_page is None:
        raise HTTPException(status_code=404, detail="Contenu non trouvé pour l'URL")
    return QualifyResponse(type_page=type_page, chunk=chunk, metadata=metadata)