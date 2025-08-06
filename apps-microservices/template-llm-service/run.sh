#!/bin/bash
source .venv/bin/activate
echo "Lancement du service Qualifier..."
uvicorn main:app --host 0.0.0.0 --port 8502 --reload
