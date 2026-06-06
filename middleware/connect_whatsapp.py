import httpx
import os
import time
import base64
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
API_KEY = os.getenv("EVOLUTION_API_KEY", "sua_apikey_global")
INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "sua_instancia")

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def create_instance():
    print(f"Buscando ou criando a instância '{INSTANCE_NAME}'...")
    try:
        response = httpx.post(
            f"{API_URL}/instance/create",
            headers=headers,
            json={
                "instanceName": INSTANCE_NAME,
                "qrcode": True,
                "integration": "WHATSAPP-BAILEYS"
            },
            timeout=10.0
        )
        
        data = response.json()
        if "instance" in data and data["instance"].get("status") in ["connecting", "close"]:
            print("Instância inicializada! Gerando QR Code...")
            time.sleep(3)
            get_connection()
            return
        if "qrcode" in data and "base64" in data["qrcode"]:
            save_qr_code(data["qrcode"]["base64"])
            return
        if response.status_code == 403 or (isinstance(data, dict) and "already exists" in str(data)):
            print("A instância já existe. Buscando o QR Code de conexão...")
            get_connection()
            return
            
        print("Resposta inesperada ao criar:", data)
    except Exception as e:
        print(f"Erro ao conectar na Evolution API: {e}. O Docker está rodando?")

def get_connection():
    try:
        response = httpx.get(
            f"{API_URL}/instance/connect/{INSTANCE_NAME}",
            headers=headers,
            timeout=10.0
        )
        data = response.json()
        
        if "base64" in data:
            save_qr_code(data["base64"])
        elif "qrcode" in data and "base64" in data["qrcode"]:
            save_qr_code(data["qrcode"]["base64"])
        elif data.get("instance", {}).get("state") == "open":
            print("O seu WhatsApp já está conectado e pronto para uso!")
        elif "error" in data:
            print(f"Erro ao buscar QR Code: {data['error']}")
        else:
            print(f"Ainda gerando QR Code ou resposta diferente da esperada. Resposta bruta: {data}")
    except Exception as e:
        print(f"Erro ao buscar conexão: {e}")

def save_qr_code(base64_string):
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
        
    image_data = base64.b64decode(base64_string)
    file_path = "qrcode.png"
    
    with open(file_path, "wb") as f:
        f.write(image_data)
        
    print(f"\n==================================================")
    print(f"SUCESSO! QR Code gerado e salvo como: {file_path}")
    print(f"Abra a imagem e escaneie com seu WhatsApp!")
    print(f"==================================================\n")

if __name__ == "__main__":
    create_instance()
