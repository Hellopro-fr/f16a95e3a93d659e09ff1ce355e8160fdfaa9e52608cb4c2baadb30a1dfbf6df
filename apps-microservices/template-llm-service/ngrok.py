import os
import asyncio
from pyngrok import ngrok, conf
import uvicorn
from main import app  # Importe votre application FastAPI depuis main.py

# --- Configuration de Ngrok ---
from google.colab import userdata
# Récupère le token depuis les secrets de Colab
NGROK_AUTH_TOKEN = userdata.get('NGROK_AUTH_TOKEN')
os.environ['NGROK_AUTHTOKEN'] = NGROK_AUTH_TOKEN
conf.get_default().auth_token = os.environ.get("NGROK_AUTHTOKEN")

# --- Lancement du serveur en asynchrone ---
async def run_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=8502, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

# Crée une tâche pour exécuter le serveur en arrière-plan.
# Le service LLM (DeepSeek) va maintenant se charger sur le GPU.
# Cette opération peut prendre 1 à 3 minutes. Soyez patient.
print("🚀 Démarrage du serveur Uvicorn...")
print("🧠 Chargement du modèle DeepSeek sur le GPU avec VLLM. Cela peut prendre quelques minutes...")
task = asyncio.create_task(run_server())

# --- Création du tunnel Ngrok ---
# Ouvre un tunnel HTTP vers le port 8502 de notre application
public_url = ngrok.connect(8502, "http")
print("="*60)
print(f"✅ Service déployé et accessible publiquement à l'adresse : {public_url}")
print(f"📚 Accédez à l'interface de test Swagger UI ici : {public_url}/docs")
print("="*60)

# Garde la cellule en exécution pour maintenir le serveur et le tunnel actifs
async def main():
    try:
        await task
    except asyncio.CancelledError:
        print("Serveur arrêté.")

asyncio.run(main())