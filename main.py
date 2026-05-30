

import os
import httpx
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import PlainTextResponse

app = FastAPI()

TOKEN_VERIFICACION = "motodomi"

# CREDENCIALES DE META
PHONE_NUMBER_ID = "1121495151051234"
META_ACCESS_TOKEN = "EAAdHCjiivpwBRvYZCg4iZBDc0VsIavlDx01YlR73qWqp8JNY6ytfb0GuD8etq1sfoxsl3l9CzRyH2EzJxZCaZCzfRIfduw2ChZA7I1Hm7XnYXPwp3ySZAx8uttXwLJ7uBH95ZACXgvEE8IZAK8D8ZBozo2zoBHBO5sXmYMG2cZAHwQOEuy8uNGQZAuJus7jDSSUZCcT3XE6FpZCMyvzctVxVEiPZCCQzFJHhh904qyMxuTpc3UdQK8VJEOCEpmFrSIjflTfMBEi4UBs5CDyiIQnMpXw4weZBXwRhwhcKdZB4YkStDAZDZD" 

@app.get("/")
@app.head("/")
def inicio():
    return {"status": "ok", "proyecto": "MOTODOMI24-7"}

@app.get("/webhook")
def verificar_webhook(
    hub_mode: str = Query(None, alias="hub.mode"), 
    hub_verify_token: str = Query(None, alias="hub.verify_token"), 
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    # Validamos usando los alias correctos con punto que envía Meta
    if hub_mode == "subscribe" and hub_verify_token == TOKEN_VERIFICACION:
        print("--- WEBHOOK VERIFICADO CON ÉXITO POR META ---")
        return PlainTextResponse(content=hub_challenge, status_code=200)
        
    print("--- INTENTO DE VERIFICACIÓN FALLIDO ---")
    return PlainTextResponse(content="Token inválido", status_code=403)

@app.post("/webhook")
async def recibir_mensajes(request: Request):
    try:
        datos = await request.json()
        print("--- NUEVO EVENTO RECIBIDO DESDE META ---")
        print(datos)
        
        # Extracción ultra-segura del teléfono
        telefono_cliente = None
        try:
            entry = datos.get("entry", [])[0]
            change = entry.get("changes", [])[0]
            value = change.get("value", {})
            
            # 1. Si es un mensaje de texto entrante del cliente
            if "messages" in value and value["messages"]:
                telefono_cliente = value["messages"][0].get("from")
            
            # 2. Si es un evento de prueba o estado de entrega (Botón de Meta)
            elif "statuses" in value and value["statuses"]:
                status_obj = value["statuses"][0]
                telefono_cliente = status_obj.get("recipient_id") or status_obj.get("id")
                if telefono_cliente and "_" in telefono_cliente:
                    telefono_cliente = telefono_cliente.split("_")[0]
            
            # Si logramos capturar un teléfono válido, respondemos
            if telefono_cliente and len(str(telefono_cliente)) > 5:
                print(f"--- ENVIANDO RESPUESTA AUTOMÁTICA AL TELÉFONO: {telefono_cliente} ---")
                await enviar_respuesta_whatsapp(telefono_cliente)
            else:
                print("El evento recibido no contiene un número de teléfono válido para responder.")
                
        except Exception as e_extract:
            print(f"Aviso en la extracción de datos: {str(e_extract)}")
            
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
