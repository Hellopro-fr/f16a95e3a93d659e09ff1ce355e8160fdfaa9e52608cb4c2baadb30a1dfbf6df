from typing import Annotated
import uuid
from pydantic import ConfigDict, BaseModel, Field
from app.schemas.base import GetBase as Base


class BaseCleaner(BaseModel):
    url: Annotated[str, Field(title="L'url du site")]
    content: Annotated[str, Field(title="Le contenu du site")]
    fetch: Annotated[bool, Field(title="Récupérer le contenu du site en utilisant fetch fonction de trafilatura ")] = False


class BaseCleanerReponse(BaseModel):
    url: Annotated[str, Field(title="L'url du site")]
    content: Annotated[str, Field(title="Le contenu du site")]

class ReponseHtml(BaseCleanerReponse):
    html: Annotated[str, Field(title="Contenu html du site si fetch contenu")]

class GetBase(BaseCleaner):
    uid: uuid.UUID
