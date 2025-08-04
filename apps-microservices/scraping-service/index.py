from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/scraping")
def read_root():
    return {"Hello": "World"}