import httpx
import os
import time
import base64
import json
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
API_KEY = os.getenv("EVOLUTION_API_KEY", "sua_apikey_global")
INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "botv25")

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}


def print_json(title, status_code, data):
    print(f"\n{title}")
    print(f"Status: {status_code}")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def save_qr_base64(base64_string):
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]

    image_data = base64.b64decode(base64_string)

    with open("qrcode.png", "wb") as f:
        f.write(image_data)

    print("\n==================================================")
    print("SUCESSO! QR Code salvo como qrcode.png")
    print("Abra a imagem e escaneie com seu WhatsApp.")
    print("==================================================\n")


def save_qr_code_text(code):
    try:
        import qrcode
    except ImportError:
        print("\nA Evolution retornou um código de QR, mas falta instalar a biblioteca qrcode.")
        print("Rode:")
        print("pip install qrcode[pil]")
        print("\nCódigo recebido:")
        print(code)
        return False

    img = qrcode.make(code)
    img.save("qrcode.png")

    print("\n==================================================")
    print("SUCESSO! QR Code gerado e salvo como qrcode.png")
    print("Abra a imagem e escaneie com seu WhatsApp.")
    print("==================================================\n")

    return True


def extract_qr(data):
    """
    Tenta encontrar QR Code em vários formatos possíveis.
    Retorna:
    - ("base64", valor)
    - ("code", valor)
    - (None, None)
    """

    if not isinstance(data, dict):
        return None, None

    # Formato direto
    if isinstance(data.get("base64"), str):
        return "base64", data["base64"]

    if isinstance(data.get("code"), str):
        return "code", data["code"]

    # Formato qrcode
    qrcode_data = data.get("qrcode")

    if isinstance(qrcode_data, dict):
        if isinstance(qrcode_data.get("base64"), str):
            return "base64", qrcode_data["base64"]

        if isinstance(qrcode_data.get("code"), str):
            return "code", qrcode_data["code"]

    if isinstance(qrcode_data, str):
        # Pode ser base64 ou código textual
        if qrcode_data.startswith("data:image") or len(qrcode_data) > 500:
            return "base64", qrcode_data
        return "code", qrcode_data

    # Formato data
    inner_data = data.get("data")

    if isinstance(inner_data, dict):
        if isinstance(inner_data.get("base64"), str):
            return "base64", inner_data["base64"]

        if isinstance(inner_data.get("code"), str):
            return "code", inner_data["code"]

        inner_qrcode = inner_data.get("qrcode")

        if isinstance(inner_qrcode, dict):
            if isinstance(inner_qrcode.get("base64"), str):
                return "base64", inner_qrcode["base64"]

            if isinstance(inner_qrcode.get("code"), str):
                return "code", inner_qrcode["code"]

        if isinstance(inner_qrcode, str):
            if inner_qrcode.startswith("data:image") or len(inner_qrcode) > 500:
                return "base64", inner_qrcode
            return "code", inner_qrcode

    return None, None


def get_connection_state():
    try:
        response = httpx.get(
            f"{API_URL}/instance/connectionState/{INSTANCE_NAME}",
            headers=headers,
            timeout=10.0
        )

        data = response.json()
        print_json("Estado da conexão:", response.status_code, data)

        return data.get("instance", {}).get("state")

    except Exception as e:
        print(f"Erro ao verificar estado da conexão: {e}")
        return None


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
            timeout=15.0
        )

        data = response.json()
        print_json("Resposta create:", response.status_code, data)

        qr_type, qr_value = extract_qr(data)

        if qr_type == "base64":
            save_qr_base64(qr_value)
            return

        if qr_type == "code":
            save_qr_code_text(qr_value)
            return

        if response.status_code == 403 and "already in use" in response.text:
            print(f"\nA instância '{INSTANCE_NAME}' já existe. Vou tentar conectar nela...")
        elif response.status_code not in [200, 201]:
            print("\nA Evolution retornou erro ao criar a instância.")
            return

        time.sleep(5)
        get_connection()

    except Exception as e:
        print(f"Erro ao conectar na Evolution API: {e}")


def get_connection():
    print(f"\nTentando buscar QR Code da instância '{INSTANCE_NAME}'...")

    state = get_connection_state()

    if state == "open":
        print("\nO WhatsApp já está conectado e pronto para uso!")
        return

    if state == "connecting":
        print("\nA instância está em 'connecting'. Vou tentar buscar o QR Code mesmo assim...")

    for i in range(10):
        try:
            response = httpx.get(
                f"{API_URL}/instance/connect/{INSTANCE_NAME}",
                headers=headers,
                timeout=10.0
            )

            data = response.json()
            print_json(f"Resposta connect tentativa {i + 1}/10:", response.status_code, data)

            qr_type, qr_value = extract_qr(data)

            if qr_type == "base64":
                save_qr_base64(qr_value)
                return

            if qr_type == "code":
                save_qr_code_text(qr_value)
                return

            state = get_connection_state()

            if state == "open":
                print("\nO WhatsApp já está conectado e pronto para uso!")
                return

            print(f"Tentativa {i + 1}/10 - QR Code ainda não veio. Aguardando...")
            time.sleep(3)

        except Exception as e:
            print(f"Erro ao buscar conexão: {e}")
            time.sleep(3)

    print("\nTempo limite esgotado.")
    print("Se a resposta continuar vindo como {'count': 0}, a instância pode estar travada.")
    print("Nesse caso, delete a instância e crie outra com um nome novo.")


if __name__ == "__main__":
    create_instance()