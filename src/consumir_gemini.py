import os
import requests
from dotenv import load_dotenv
import time
import json
import re

load_dotenv()

#Constantes
MODELO = "gemini-3.5-flash-lite"
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
API_KEY = os.getenv("GEMINI_API_KEY")
PRECIO_ENTRADA = 0.0000003
PRECIO_SALIDA = 0.0000025

#función para crear la solicitud
def armar_peticion(pregunta, system_instruction, response_schema=None, modelo=MODELO):
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía")
    url = f"{URL_BASE}{modelo}:generateContent?key={API_KEY}"
    body = {
        "systemInstruction": {
            "parts": [ {"text": system_instruction} ]
        },
        "contents": [
            {"parts": [{"text": pregunta}]}
        ]
    }
    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
    }
    return url, body

#función envía la petición
def enviar_peticion(url, body):
    try:
        respuesta = requests.post(url, json=body, timeout=30)

    except requests.exceptions.Timeout as error:
        raise TimeoutError(
            "Se agotó el tiempo de espera del proveedor."
        ) from error

    except requests.exceptions.ConnectionError as error:
        raise RuntimeError(
            "No se pudo conectar con el servicio."
        ) from error

    if respuesta.status_code in(401, 403):
        raise ValueError("Credencial inválida o sin permiso. Revisa tu GEMINI_API_KEY")

    if respuesta.status_code >= 500:
        raise TimeoutError("El proveedor no pudo procesar la petición. Hay que esperar y reintintar")
    
    if respuesta.status_code == 429:
        try:
            detalle = respuesta.json()["error"]["message"]
        except (ValueError, KeyError, TypeError):
            detalle = "El proveedor informó un límite de uso."

        if not isinstance(detalle, str) or not detalle.strip():
            detalle = "El proveedor informó un límite de uso."

        segundos = respuesta.headers.get("Retry-After")
        
        if segundos:
            detalle += f" Reintentar después de {segundos} segundos."

        raise TimeoutError(f"HTTP 429: {detalle}")
    
    if respuesta.status_code != 200:
        raise RuntimeError(f"Error en la petición. Status Code: {respuesta.status_code}")
    
    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")

#función procesa y extrae dato
def extraer_texto(datos):#Gemini
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no recibe el texto generado en el lugar definido.")

def obtener_dato_de_prueba(pregunta):
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "instrumento": {
                "type": "STRING",
                "enum": ["bateria_electronica"],
            },
            "nivel": {
                "type": "STRING",
                "enum": ["principiante", "intermedio", "avanzado"],
            },
            "objetivo_practica": {"type": "STRING"},
            "duracion_real_minutos": {"type": "NUMBER"},
            "bpm": {"type": "INTEGER"},
            "sesion_completada": {"type": "BOOLEAN"},
            "dificultad_observada": {"type": "STRING"},
            "molestia_reportada": {"type": "BOOLEAN"},
        },
        "required": [
            "instrumento",
            "nivel",
            "objetivo_practica",
            "duracion_real_minutos",
            "bpm",
            "sesion_completada",
            "dificultad_observada",
            "molestia_reportada",
        ],
    }
    system_instruction = (
        "Eres RhythmMentor y organizas registros de práctica de batería. "
        "Extrae únicamente la información que la persona proporcionó; no inventes "
        "datos ni agregues recomendaciones. Devuelve solo un objeto JSON que cumpla "
        "el esquema indicado. Marca molestia_reportada como true solo si la persona "
        "menciona explícitamente dolor o molestias."
    )
    claves_esperadas = [
        "instrumento",
        "nivel",
        "objetivo_practica",
        "duracion_real_minutos",
        "bpm",
        "sesion_completada",
        "dificultad_observada",
        "molestia_reportada",
    ]
    url, body = armar_peticion(pregunta, system_instruction, response_schema, MODELO) #obtiene url y body

    inicio = time.perf_counter() #Empieza el contador

    datos = enviar_peticion(url, body)

    fin = time.perf_counter() #Termina el contador
    latencia = fin - inicio
    print("Modelo: ", MODELO)
    print(f"Latencia: {latencia:.2f} segundos")
    costo,total_tokens = calcular_costos(datos, PRECIO_ENTRADA, PRECIO_SALIDA)
    print(f"Costo de la petición: ${costo:.6f} USD, total Tokens: {total_tokens}")
    texto = extraer_texto(datos)
    datos_formateados = parsear_respuesta_json(texto, claves_esperadas=claves_esperadas)
    return datos_formateados

#def calcular_costos(datos:dict, precio_entrda: float, precio_salida: float) -> float:
def calcular_costos(datos, precio_entrada, precio_salida):
    #datos = {dict... "usageMetadata"}
    uso = datos.get("usageMetadata") if isinstance(datos, dict) else None
    if not isinstance(uso, dict):
        raise RuntimeError("La respuesta no incluye datos de uso para calcular el costo.")
    '''
    uso = {
        "promptTokenCount": 33,
        "candidatesTokenCount": 401,
        "totalTokenCount": 1470,
        "promptTokensDetails": [
            {
                "modality": "TEXT",
                "tokenCount": 33
            }
        ],
        "thoughtsTokenCount": 1036,
        "serviceTier": "standard"
    }
    '''
    try:
        tokens_entrada = uso["promptTokenCount"]
        tokens_salida = uso["candidatesTokenCount"]
        total_tokens = uso["totalTokenCount"]
    except KeyError:
        raise RuntimeError("Faltan los tokens de entrada o salida para calcular el costo.") from None
    tokens_razonamiento = uso.get("thoughtsTokenCount", 0)
    for tokens in (
        tokens_entrada, 
        tokens_salida, 
        tokens_razonamiento,
        total_tokens,
    ):
        if type(tokens) is not int or tokens < 0:
            raise RuntimeError("Los datos de tokens deben ser números enteros no negativos.")
    costo = (tokens_entrada * precio_entrada) + ((tokens_salida + tokens_razonamiento) * precio_salida)
    return costo, total_tokens

def parsear_respuesta_json(texto, claves_esperadas=None):
    texto_limpio = texto.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)

    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError:
        raise ValueError(
            "La respuesta del modelo no es JSON válido."
        ) from None

    if not isinstance(datos, dict):
        raise ValueError("La respuesta JSON debe ser un objeto.")

    if claves_esperadas:
        faltantes = [
            clave for clave in claves_esperadas
            if clave not in datos
        ]
        if faltantes:
            raise ValueError(
                "La respuesta no tiene la estructura esperada."
            )

    return datos

if __name__ == "__main__":
    try:
        pregunta = (
            "Registra esta sesión: soy principiante en batería electrónica. "
            "Practiqué coordinación entre manos y pies durante 8 minutos a 60 BPM. "
            "Terminé el ejercicio, pero me adelanté al usar el pie izquierdo. "
            "No sentí dolor ni molestias."
        )
        print(obtener_dato_de_prueba(pregunta))
    except (ValueError, RuntimeError, TimeoutError) as error:
        print("No se pudo completar la operación: ", error)
