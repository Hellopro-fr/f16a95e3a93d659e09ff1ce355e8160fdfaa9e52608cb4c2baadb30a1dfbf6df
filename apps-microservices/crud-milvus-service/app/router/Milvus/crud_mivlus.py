from fastapi import APIRouter, HTTPException
from app.schemas.Milvus.Produit import InsertProduitRequest, UpdateProduitRequest, DeleteProduitRequest, ProduitResponse
from app.core.Milvus.CrudProduitMilvus import CrudProduitMilvus

router = APIRouter()

@router.get("/produit")
def get(id_produit: str):
    try:
        crud_milvus_service = CrudProduitMilvus()
        produits = crud_milvus_service.get_produit(id_produit)

        print(produits)

        # ⚠️ S'assurer que "data" est bien retourné
        return produits

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/produit" ,response_model=ProduitResponse)
def create(request: InsertProduitRequest):
    try:
        crud_milvus_service = CrudProduitMilvus()
        state_insertion = crud_milvus_service.insert_produit(request.dict())

        print(state_insertion)

        # ⚠️ S'assurer que "data" est bien retourné
        return {"data": state_insertion}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/produit" ,response_model=ProduitResponse)
def update(request: UpdateProduitRequest):
    try:
        crud_milvus_service = CrudProduitMilvus()
        state_update = crud_milvus_service.update_produit(request.dict())

        # ⚠️ S'assurer que "data" est bien retourné
        return {"data": state_update}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/produit" ,response_model=ProduitResponse)
def delete(request: DeleteProduitRequest):
    try:
        crud_milvus_service = CrudProduitMilvus()
        state_update = crud_milvus_service.delete_produit(request.dict())

        # ⚠️ S'assurer que "data" est bien retourné
        return {"data": state_update}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
