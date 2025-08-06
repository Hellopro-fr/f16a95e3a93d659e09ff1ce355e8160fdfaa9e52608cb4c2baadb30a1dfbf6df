from fastapi import APIRouter, HTTPException
from app.schemas.qualifier.qualifier import QualifyRequest, QualifyResponse
from app.core.qualifier.Qualifier import QualifierService

router = APIRouter()

@router.post("/", response_model=QualifyResponse)
async def qualify(request: QualifyRequest):
    service = QualifierService()
    type_page, chunk, metadata = service.classify(request.url)
    if type_page is None:
        raise HTTPException(status_code=404, detail="Contenu non trouvé pour l'URL")
    return QualifyResponse(type_page=type_page, chunk=chunk, metadata=metadata)
