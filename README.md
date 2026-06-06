# Assistente Virtual Inteligente (Botpress + WhatsApp)

Este projeto é uma solução completa de Agente Conversacional (Chatbot) integrado ao WhatsApp. A arquitetura foi desenvolvida como parte de um desafio técnico para conectar o fluxo lógico de uma inteligência artificial criada no **Botpress Cloud** com o WhatsApp através da **Evolution API v2**.

O projeto também conta com uma ponte customizada (**Middleware** em Python) que intermedia, formata e roteia as mensagens entre a API do WhatsApp e a API do Botpress.

---

## Arquitetura do Projeto

A solução é composta por 3 pilares principais:

1. **Botpress Cloud:** O "Cérebro" do bot. Responsável por processar a linguagem natural, buscar respostas na Base de Conhecimento (Currículo e informações da empresa) e usar o ChatGPT para gerar respostas dinâmicas.
2. **Evolution API v2:** O "Motor do WhatsApp". Roda localmente via Docker e faz a conexão direta com o aplicativo do WhatsApp através da leitura de QR Code.
3. **Middleware Python:** A "Ponte". Um servidor local construído com FastAPI que recebe os webhooks da Evolution API, trata os dados, envia para a API do Botpress, aguarda o processamento da IA e envia a resposta de volta ao WhatsApp do usuário final.

---

## Tecnologias Utilizadas

- **Linguagem Principal:** Python 3.10+
- **Framework Web:** FastAPI (para recebimento rápido de Webhooks) e Uvicorn
- **Requisições HTTP:** `httpx` (Assíncrono para garantir alta performance)
- **Mensageria WhatsApp:** Evolution API v2 (Docker + Redis + PostgreSQL)
- **Plataforma de IA:** Botpress Cloud API

---

## Como testar localmente na sua máquina

Siga os passos abaixo para rodar o projeto e conectar o seu próprio WhatsApp.

### Pré-requisitos
- Docker e Docker Compose instalados.
- Python 3.10 ou superior.

### Passo 1: Subir a Evolution API
Navegue até a pasta `evolution` e suba os containers do banco de dados, Redis e da API:
```bash
cd evolution
docker-compose up -d
```
A API do WhatsApp estará rodando em `http://localhost:8080`.

### Passo 2: Configurar o Middleware
Navegue até a pasta `middleware` e crie um ambiente virtual para instalar as dependências:
```bash
cd ../middleware
python -m venv venv
venv\Scripts\activate  # No Windows
pip install fastapi uvicorn httpx
```

### Passo 3: Variáveis de Ambiente
Verifique o arquivo `.env` na pasta `middleware` e garanta que o `BOTPRESS_WEBHOOK_ID` está preenchido com a sua integração Webchat do Botpress.

```env
BOTPRESS_WEBHOOK_ID=seu_id_aqui
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=sua_apikey_global
EVOLUTION_INSTANCE_NAME=botv4
```

### Passo 4: Rodar o Servidor
Inicie o middleware Python que ficará escutando as mensagens:
```bash
python main.py
```

### Passo 5: Conectar o WhatsApp
Em um novo terminal, dentro da pasta `middleware`, rode o script automático para criar a instância e gerar o QR Code no seu terminal:
```bash
python connect_whatsapp.py
```
Abra o WhatsApp no seu celular, vá em "Aparelhos Conectados" e escaneie o QR Code que aparecerá no console. Em seguida, rode o script de webhook:
```bash
python configure_webhook.py
```

Pronto! Basta enviar uma mensagem para o número conectado e o Botpress começará a responder automaticamente.

---

##  Testando a versão em Produção (Telegram)

Para fins de avaliação rápida e demonstração online (24/7), o fluxo de Inteligência Artificial construído no Botpress também foi integrado ao **Telegram**.

Dessa forma, o avaliador não precisa subir a infraestrutura local (Docker/Evolution API) para interagir com o bot. 
Basta acessar o link abaixo e mandar um "Oi" para conversar com o assistente instantaneamente:

  **[Acessar o Bot no Telegram](https://t.me/ProjetoB2B_bot)**
