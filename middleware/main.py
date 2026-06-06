from fastapi import FastAPI, Request
from dotenv import load_dotenv
import os

from botpress_client import BotpressClient
from evolution_client import EvolutionClient

load_dotenv()

app = FastAPI(title="Botpress <-> Evolution API Middleware")

botpress_client = BotpressClient()
evolution_client = EvolutionClient()

@app.post("/webhook/evolution")
async def evolution_webhook(request: Request):
    payload = await request.json()
    
    print(f"\n[DEBUG] Payload recebido: {payload}")
    
    if not payload.get("data"):
        return {"status": "ignored", "reason": "No data in payload"}
        
    if "messages" in payload["data"] and isinstance(payload["data"]["messages"], list) and len(payload["data"]["messages"]) > 0:
        message_data = payload["data"]["messages"][0]
    else:
        message_data = payload["data"]
    
    connected_phone = payload.get("sender", "")
    sender_phone = message_data.get("key", {}).get("remoteJid", "")
    
    if message_data.get("fromMe") or message_data.get("key", {}).get("fromMe"):
        if sender_phone != connected_phone and sender_phone != "279362003849241@lid":
            return {"status": "ignored", "reason": "Message from self to others"}
        
    sender_phone = message_data.get("key", {}).get("remoteJid")
    if not sender_phone:
        return {"status": "ignored", "reason": "No sender phone"}
        
    if "@g.us" in sender_phone:
        return {"status": "ignored", "reason": "Group message ignored"}
        
    message_type = message_data.get("messageType")
    text = ""
    
    if message_type == "conversation":
        text = message_data.get("message", {}).get("conversation", "")
    elif message_type == "extendedTextMessage":
        text = message_data.get("message", {}).get("extendedTextMessage", {}).get("text", "")
    else:
        print(f"Tipo de mensagem não suportado: {message_type}")
        return {"status": "ignored", "reason": "Unsupported message type"}
        
    if not text:
        return {"status": "ignored", "reason": "Empty text"}
        
    print(f"\n[WhatsApp -> Middleware] Mensagem recebida de {sender_phone}: {text}")
    
    print(f"[Middleware -> Botpress] Enviando texto para o Botpress...")
    botpress_response = await botpress_client.send_message(sender_phone, text)
    
    if botpress_response:
        for bp_msg in botpress_response:
            if bp_msg.get("type") == "text":
                response_text = bp_msg.get("text", "")
                
                # Se for o chat "Você" (termina com @lid), a Evolution não consegue enviar para o @lid.
                # Devemos enviar para o próprio número conectado (connected_phone).
                reply_phone = sender_phone
                if sender_phone == "279362003849241@lid" and connected_phone:
                    reply_phone = connected_phone
                    
                print(f"[Middleware -> WhatsApp] Enviando resposta para {reply_phone}: {response_text}")
                await evolution_client.send_text_message(reply_phone, response_text)
                
    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
