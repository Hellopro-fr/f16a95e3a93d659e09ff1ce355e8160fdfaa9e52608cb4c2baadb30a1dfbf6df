#!/bin/bash

source .venv/bin/activate
# pip install -r requirements.txt

uvicorn index:app --host 0.0.0.0 --port 8502 --reload
