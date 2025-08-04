import json
import os
from typing import Annotated
import uuid

from click import File
from fastapi import APIRouter, Depends, Form, HTTPException, status, UploadFile
from app.core.files.files import check_mimetype, generate_filename

from app.schemas.message import GetEmptyResponse, GetResponse
from app.schemas.cleaner.cleaner import BaseCleaner as BaseData
from app.utils.response import error_response, success_response
from app.core.cleaner.TrafilaturaHp import TrafilaturaHp
from app.core.credentials import settings

router = APIRouter()

@router.post("/")
async def clean(datas: list[BaseData]):
    trafila = TrafilaturaHp()
    trafila.info = datas
    return trafila.extract()

# @router.post("/files")
# async def upload(files: Annotated[list[UploadFile], File()]):
#     result = {}

#     for file in files:
#         content_bytes = await file.read()
#         try:
#             # Decode bytes to str, then parse JSON
#             content_str = content_bytes.decode('utf-8')
#             data_entries = json.loads(content_str)
#         except json.JSONDecodeError:
#             result[file.filename] = {"error": f"ERREUR: Impossible de décoder le JSON du fichier {file.name}. Fichier ignoré."}
#             continue
#         except Exception as e:
#             result[file.filename] = {"error": f"Failed to parse JSON: {e}"}
#             continue
        
#         # Assign to trafila.info and extract
#         print(data_entries[0]["url"])
#         result[file.filename] = await clean(data_entries)

#     return result