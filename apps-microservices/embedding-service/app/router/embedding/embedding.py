from fastapi import APIRouter, HTTPException
from app.schemas.embedding.embedding import EmbedRequest, EmbedResponse
from app.core.embedding.Embedding import Embedding

router = APIRouter()

@router.post("/", response_model=EmbedResponse)
def embed(request: EmbedRequest):
    try:
        embedding_service = Embedding()
        embeddings = embedding_service.embed_data_clean(request.dict())

        print(embeddings)

        # ⚠️ S'assurer que "data" est bien retourné
        return {"data": embeddings}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
