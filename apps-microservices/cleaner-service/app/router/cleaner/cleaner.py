import json
import os
from typing import Annotated, List
import uuid

from click import File
from fastapi import APIRouter, Depends, Form, HTTPException, status, UploadFile
from app.core.files.files import check_mimetype, generate_filename

from app.schemas.message import GetEmptyResponse, GetResponse
from app.schemas.cleaner.cleaner import BaseTrafilatura as BaseData, BaseTrafilaturaReponse, TrafilaturaReponseHtml
from app.utils.response import error_response, success_response
from app.core.cleaner.TrafilaturaHp import TrafilaturaHp
from app.core.credentials import settings

router = APIRouter()

@router.post("/trafilatura")
async def clean(datas: list[BaseData]) -> List[BaseTrafilaturaReponse | TrafilaturaReponseHtml]:
    trafila = TrafilaturaHp()
    trafila.info = datas
    return trafila.extract()