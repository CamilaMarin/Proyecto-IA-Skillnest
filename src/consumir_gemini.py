import os
import requests
from dotenv import load_dotenv

import time

load_dotenv()

#Constantes
MODELO = "gemini-3.6-flash"
URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
API_KEY = os.getenv("GEMINI_API_KEY")
PRECIO_ENTRADA = 0.00000075
PRECIO_SALIDA = 0.00000375

#función para crear la solicitud
def armar_peticion(pregunta, modelo=MODELO):
    if not pregunta:
        raise ValueError("La pregunta no puede estar vacía")
    url = f"{URL_BASE}{modelo}:generateContent?key={API_KEY}"
    body = {
        "contents": [
            {"parts": [{"text": pregunta}]}
        ]
    }
    return url, body

#función envía la petición
def enviar_peticion(url, body):
    try:
        respuesta = requests.post(url, json=body, timeout=30)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No se pudo conectar con el servidor. Intenta de nuevo en unos momentos.")
    except requests.exceptions.Timeout:
        raise RuntimeError("Se agotó el tiempo. Intenta de nuevo en unos momentos.")

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
    url, body = armar_peticion(pregunta)

    inicio = time.perf_counter() #Empieza el contador

    datos = enviar_peticion(url, body)

    fin = time.perf_counter() #Termina el contador
    latencia = fin - inicio
    print("Modelo: ", MODELO)
    print(f"Latencia: {latencia:.2f} segundos")
    costo = calcular_costos(datos, PRECIO_ENTRADA, PRECIO_SALIDA)
    print(f"Costo de la petición: ${costo:.6f} USD")
    return extraer_texto(datos)

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
    except KeyError:
        raise RuntimeError("Faltan los tokens de entrada o salida para calcular el costo.") from None
    tokens_razonamiento = uso.get("thoughtsTokenCount", 0)
    for tokens in (tokens_entrada, tokens_salida, tokens_razonamiento):
        if type(tokens) is not int or tokens < 0:
            raise RuntimeError("Los datos de tokens deben ser números enteros no negativos.")
    costo = (tokens_entrada * precio_entrada) + ((tokens_salida + tokens_razonamiento) * precio_salida)
    return costo

if __name__ == "__main__":
    try:
        print(obtener_dato_de_prueba("Soy principiante en batería electrónica. Tengo 20 minutos disponibles y quiero Mejorar la coordinación entre manos y pies. Mi tempo inicial es 60 BPM. Genera una sesión estructurada con ejercicios, duración, instrucciones y objetivos. La duración total debe ser exactamente 20 minutos."))
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación: ", error)
