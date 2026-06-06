import httpx
import os

class EvolutionClient:
    def __init__(self):
        self.base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        
        self.api_key = os.getenv("EVOLUTION_API_KEY", "SUA_API_KEY_AQUI")
        
        self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "bot-instance")

    async def send_text_message(self, phone_number: str, text: str):
        url = f"{self.base_url}/message/sendText/{self.instance_name}"
        
        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Se o número já tiver o domínio (@lid, @g.us, @s.whatsapp.net), não removemos!
        clean_number = phone_number
        
        payload = {
            "number": clean_number,
            "text": text,
            "delay": 1200
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                if response.status_code not in [200, 201]:
                    print(f"[Erro Evolution API] Status {response.status_code} - {response.text}")
                return response.json()
            except Exception as e:
                print(f"[Erro Evolution API] Falha na conexão: {e}")
                return None
