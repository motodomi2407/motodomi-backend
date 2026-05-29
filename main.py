


import os
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse

app = FastAPI()

TOKEN_VERIFICACION = "MiCodigoSecretoMotoDomi2026"

# CREDENCIALES DE META (Cambia esto con tus datos)
PHONE_NUMBER_ID = "1121495151051234"
META_ACCESS_TOKEN = EAAdHCjiivpwBRjoZAVAojrWygDq77zQIRIQeONXcj4pDk6zLQmPa3Ra5pEP8nPVSRPpBEQQQRC09RZBosQegb7IGRnBNqxfqT9DBiZAURh7RgfMyvsY9TUSIWFRS32zTZA9M1mBkpZAUgOPf5qNwVwjHUZBsDQfdl66KBWAANF9RKs4g6QYM5ZAyeEG4F2nbSHOBNpPvXtgV2BPfhwAnQTSWuUSg0QX8jpDOUM64jsBWgohkuOIqRFEqRRru9WhEcC6m2qHW4oY62PoRf29AvZB9vYnpe1TmpV3PW0kZAbgZDZD

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
    try:
        datos = await request.json()
        
        if "entry" in datos and datos["entry"]:
            changes = datos["entry"][0].get("changes", [])
            if changes and "value" in changes[0]:
                value = changes[0]["value"]
                if "messages" in value and value["messages"]:
                    mensaje_data = value["messages"][0]
                    
                    telefono_cliente = mensaje_data.get("from")
                    texto_mensaje = mensaje_data.get("text", {}).get("body", "")
                    
                    print(f"--- NUEVO MENSAJE DE MOTODOMI ---")
                    print(f"Cliente: {telefono_cliente}")
                    print(f"Texto: {texto_mensaje}")
                    print(f"---------------------------------")
                    
                    # AQUÍ LE RESPONDEMOS AUTOMÁTICAMENTE
                    await enviar_respuesta_whatsapp(telefono_cliente, "¡Hola! 🏍️ Bienvenido a MOTODOMI24-7. Tu mensaje fue recibido en nuestro sistema backend. En breve procesaremos tu solicitud.")
                    
    except Exception as e:
        print("Error al procesar el JSON de Meta:", str(e))
        
    return {"status": "EVENT_RECEIVED"}

async def enviar_respuesta_whatsapp(telefono_destino: str, texto_respuesta: str):
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono_destino,
        "type": "text",
        "text": {"body": texto_respuesta}
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                print(f"Respuesta enviada con éxito a {telefono_destino}")
            else:
                print(f"Error al enviar a Meta: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Fallo en la conexión al enviar mensaje: {str(e)}")
