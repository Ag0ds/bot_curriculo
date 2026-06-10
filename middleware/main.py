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
    
    if not payload.get("data") and not payload.get("qrcode"):
        return {"status": "ignored", "reason": "No data in payload"}
        
    event_name = payload.get("event", "")
    if event_name != "messages.upsert":
        return {"status": "ignored", "reason": f"Event {event_name} ignored"}

    data_payload = payload.get("data", {})
    
    if isinstance(data_payload, list):
        if len(data_payload) > 0:
            message_data = data_payload[0]
        else:
            return {"status": "ignored", "reason": "Empty list in data"}
    elif isinstance(data_payload, dict) and "messages" in data_payload and isinstance(data_payload["messages"], list) and len(data_payload["messages"]) > 0:
        message_data = data_payload["messages"][0]
    else:
        message_data = data_payload
    sender_phone = message_data.get("key", {}).get("remoteJid", "")

    if message_data.get("key", {}).get("fromMe"):
        return {"status": "ignored", "reason": "Message from self"}

    # Filtro para ignorar mensagens antigas (mais de 2 minutos atrás)
    import time
    message_timestamp = int(message_data.get("messageTimestamp", 0))
    current_time = int(time.time())
    if current_time - message_timestamp > 120:
        print(f"[Ignorado] Mensagem antiga de {sender_phone} ignorada.")
        return {"status": "ignored", "reason": "Message is too old"}

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
                
                reply_phone = sender_phone

                print(f"[Middleware -> WhatsApp] Enviando resposta para {reply_phone}: {response_text}")
                await evolution_client.send_text_message(reply_phone, response_text)
                
    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
