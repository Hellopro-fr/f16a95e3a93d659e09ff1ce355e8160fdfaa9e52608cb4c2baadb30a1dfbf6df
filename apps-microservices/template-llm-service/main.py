import logging
import os
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.utils.params import params
from app.utils.response import error_response

description = "API Qualifier [Classification de pages fournisseurs] 🚀"

os.makedirs("logs", exist_ok=True)

app = FastAPI(title="API Qualifier", description=description, version="v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="logs/qualifier.log",
    filemode="a"
)

@app.exception_handler(Exception)
async def error_handler(request: Request, exc: Exception):
    logging.error(str(exc))
    return error_response("EXCEPTION_ERROR", f"{exc}", status.HTTP_500_INTERNAL_SERVER_ERROR)

for item in params:
    app.include_router(
        item[0],
        prefix=item[1],
        tags=item[2],
        include_in_schema=item[3]
    )

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API Qualifier",
        description=description,
        version="v1",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": "statics/qualifier-logo.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
