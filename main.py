


import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse

app = FastAPI()

TOKEN_VERIFICACION = "MiCodigoSecretoMotoDomi2026"

@app.get("/webhook")
async def verificar_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == TOKEN_VERIFICACION:
            print("¡Webhook verificado con éxito por Meta!")
            return PlainTextResponse(content=challenge, status_code=200)
        else:
            return Response(content="Token de verificación inválido", status_code=403)
            
    return Response(content="Faltan parámetros", status_code=400)

@app.post("/webhook")
async def recibir_mensajes(request: Request):
    datos = await request.json()
    print("Mensaje recibido de WhatsApp:", datos)
    return {"status": "EVENT_RECEIVED"}
