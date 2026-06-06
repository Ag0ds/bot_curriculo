import httpx
import os
import uuid

class BotpressClient:
    def __init__(self):
        self.webhook_id = os.getenv("BOTPRESS_WEBHOOK_ID")
        self.base_url = f"https://chat.botpress.cloud/{self.webhook_id}"
    
        self.sessions = {}

    async def get_or_create_session(self, phone_number: str):
        if phone_number in self.sessions:
            return self.sessions[phone_number]

        async with httpx.AsyncClient() as client:
            user_response = await client.post(f"{self.base_url}/users", json={})
            user_data = user_response.json()
            if "user" not in user_data:
                print(f"[Erro Botpress] Falha ao criar usuário. Verifique se o seu BOTPRESS_WEBHOOK_ID está correto e ativo! Resposta: {user_data}")
                return None
                
            user_id = user_data["user"]["id"]
            user_key = user_data.get("key") 

            headers = {"x-user-key": user_key}

            conv_response = await client.post(f"{self.base_url}/conversations", headers=headers, json={})
            conv_data = conv_response.json()
            conversation_id = conv_data["conversation"]["id"]

            session = {
                "user_id": user_id,
                "x_user_key": user_key,
                "conversation_id": conversation_id
            }
            self.sessions[phone_number] = session
            return session

    async def send_message(self, phone_number: str, text: str):
        if not self.webhook_id:
            print("[Erro] BOTPRESS_WEBHOOK_ID não configurado no .env")
            return None

        session = await self.get_or_create_session(phone_number)
        if not session:
            return None
        
        headers = {"x-user-key": session["x_user_key"]}
        payload = {
            "conversationId": session["conversation_id"],
            "payload": {
                "type": "text",
                "text": text
            }
        }

        async with httpx.AsyncClient() as client:
            
            response = await client.post(f"{self.base_url}/messages", headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                import asyncio
                
                print("[Botpress] Aguardando a IA processar e responder (até 10s)...")
                
                bot_messages = []
                for _ in range(5):
                    await asyncio.sleep(2)
                    
                    response = await client.get(
                        f"{self.base_url}/conversations/{session['conversation_id']}/messages",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        all_messages = response.json().get("messages", [])
                        bot_messages = [msg.get("payload") for msg in all_messages if msg.get("userId") != session["user_id"]]
                        
                        if len(bot_messages) > 0:
                            break  # Achou a resposta! Sai do loop.
                            
                print(f"[DEBUG Botpress] Total de mensagens finais: {len(all_messages)}")
                print(f"[DEBUG Botpress] Mensagens do Bot: {bot_messages}")
                
                return bot_messages[:1] 
            else:
                print(f"[Erro Botpress] {response.text}")
                return None
