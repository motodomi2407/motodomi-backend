


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
    try:
        datos = await request.json()
        
        # Verificamos que el JSON contenga un mensaje válido
        if "entry" in datos and datos["entry"]:
            changes = datos["entry"][0].get("changes", [])
            if changes and "value" in changes[0]:
                value = changes[0]["value"]
                if "messages" in value and value["messages"]:
                    mensaje_data = value["messages"][0]
                    
                    # Extraemos la información clave
                    telefono_cliente = mensaje_data.get("from")
                    texto_mensaje = mensaje_data.get("text", {}).get("body", "")
                    
                    # Lo imprimimos bonito en la consola de Render
                    print(f"--- NUEVO MENSAJE DE MOTODOMI ---")
                    print(f"Cliente: {telefono_cliente}")
                    print(f"Texto: {texto_mensaje}")
                    print(f"---------------------------------")
                    
    except Exception as e:
        print("Error al procesar el JSON de Meta:", str(e))
        
    return {"status": "EVENT_RECEIVED"}
