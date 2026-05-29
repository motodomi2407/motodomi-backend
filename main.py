

import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse

app = FastAPI()

TOKEN_VERIFICACION = "MiCodigoSecretoMotoDomi2026"

# CREDENCIALES DE META
PHONE_NUMBER_ID = "1121495151051234"
META_ACCESS_TOKEN = "EAAdHCjiivpwBRpzRr9dg5nKDK89om6qyTZBMGITa8K7ZARVPNOLmOdZCePnzLlIpecqTZAxAlnfYU3UJ4Th6IVi8OzKf5Eod3uR18Vh7G0XRMjI1KHyUzqvnqEmHrVm4GrxeFTN70w5SbPxXwQFPlkMdo4ZCfPxyBUENx2UeeYeDMbRCnsiQH60LIc6aoa29ZCdb0jjcNDdbkaxPKqL240apDjiG6LerWZBqsyK86DZCZACH8TzwUoLJIElxoqXgW2DLEoaKyX2dZALZCbcLyTnXm3tZCf4JPpLuPvKBWWoZCnAZDZD" 

@app.get("/")
@app.head("/")
def inicio():
    return {"status": "ok", "proyecto": "MOTODOMI24-7"}

@app.get("/webhook")
async def verificar_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    if mode and token:
        if mode == "subscribe" and token == TOKEN_VERIFICACION:
            print("--- WEBHOOK VERIFICADO CON ÉXITO POR META ---")
            return PlainTextResponse(content=challenge, status_code=200)
    return Response(content="Faltan parámetros o token inválido", status_code=400)

@app.post("/webhook")
async def recibir_mensajes(request: Request):
    try:
        datos = await request.json()
        print("--- NUEVO EVENTO RECIBIDO DESDE META ---")
        print(datos) # Esto nos mostrará el JSON exacto en Render
        
        # Extracción segura y directa del número de teléfono
        try:
            entry = datos.get("entry", [])[0]
            change = entry.get("changes", [])[0]
            value = change.get("value", {})
            
            # Buscamos el teléfono ya sea de un mensaje o de un estado de entrega
            telefono_cliente = None
            if "messages" in value:
                telefono_cliente = value["messages"][0].get("from")
            elif "statuses" in value:
                telefono_cliente = value["statuses"][0].get("recipient_id")
                
            if telefono_cliente:
                print(f"--- ENVIANDO RESPUESTA AUTOMÁTICA AL TELÉFONO: {telefono_cliente} ---")
                await enviar_respuesta_whatsapp(telefono_cliente)
                
        except Exception as e_extract:
            print(f"No se pudo extraer teléfono de la estructura (evento interno de Meta): {str(e_extract)}")
            
        return Response(content="EVENT_RECEIVED", status_code=200)
    except Exception as e:
        print(f"--- ERROR CRÍTICO AL PROCESAR: {str(e)} ---")
        return Response(content="Error interno", status_code=500)

async def enviar_respuesta_whatsapp(telefono):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono,
        "type": "text",
        "text": {
            "body": "¡Hola! 🏍️ Bienvenido a MOTODOMI24-7.\n\nTu mensaje fue recibido con éxito en nuestro sistema. En un momento uno de nuestros asesores o mototaxistas se pondrá en contacto contigo para coordinar tu servicio.\n\n¡Gracias por confiar en nosotros!"
        }
    }
    
    async with httpx.AsyncClient() as client:
        respuesta = await client.post(url, json=payload, headers=headers)
        print(f"--- RESPUESTA DE META AL ENVIAR: {respuesta.status_code} ---")
        print(respuesta.text)
