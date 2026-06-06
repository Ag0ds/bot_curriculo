import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
API_KEY = os.getenv("EVOLUTION_API_KEY", "sua_apikey_global")
INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "botv4")

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def configure_webhook():
    print(f"Configurando webhook para a instancia '{INSTANCE_NAME}'...")
    webhook_url = "http://host.docker.internal:8000/webhook/evolution"
    
    payload = {
        "webhook": {
            "enabled": True,
            "url": webhook_url,
            "webhook_by_events": False,
            "webhook_base64": False,
            "events": [
                "APPLICATION_STARTUP",
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE"
            ]
        }
    }
    
    try:
        response = httpx.post(
            f"{API_URL}/webhook/set/{INSTANCE_NAME}",
            headers=headers,
            json=payload
        )
        
        if response.status_code in [200, 201]:
            print(f"Webhook configurado com sucesso! As mensagens serao enviadas para {webhook_url}")
        else:
            print(f"Falha ao configurar webhook. Status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Erro ao configurar webhook: {e}")

if __name__ == "__main__":
    configure_webhook()
