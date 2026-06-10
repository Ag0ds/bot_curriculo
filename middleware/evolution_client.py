import httpx
import os
import re


class EvolutionClient:
    def __init__(self):
        self.base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        self.api_key = os.getenv("EVOLUTION_API_KEY", "sua_apikey_global")
        self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "botv25")

    def normalize_number(self, phone_number: str) -> str:
        if not phone_number:
            return ""

        if "@s.whatsapp.net" in phone_number:
            return phone_number.split("@")[0]

        if "@g.us" in phone_number:
            return ""

        if "@lid" in phone_number:
            print(f"[Aviso] Número veio como @lid e pode não ser possível responder diretamente: {phone_number}")
            return phone_number

        return re.sub(r"\D", "", phone_number)

    async def send_text_message(self, phone_number: str, text: str):
        url = f"{self.base_url}/message/sendText/{self.instance_name}"

        clean_number = self.normalize_number(phone_number)

        if not clean_number:
            print("[Erro Evolution API] Número vazio ou inválido.")
            return None

        headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "number": clean_number,
            "text": text,
            "options": {
                "delay": 1200
            }
        }

        print(f"[DEBUG Evolution] URL: {url}")
        print(f"[DEBUG Evolution] Enviando para: {clean_number}")
        print(f"[DEBUG Evolution] Payload: {payload}")

        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)

                print(f"[DEBUG Evolution] Status: {response.status_code}")
                print(f"[DEBUG Evolution] Resposta: {response.text}")

                if response.status_code not in [200, 201]:
                    print(f"[Erro Evolution API] Status {response.status_code} - {response.text}")
                    return None

                return response.json()

            except Exception as e:
                print(f"[Erro Evolution API] Falha na conexão: {e}")
                return None