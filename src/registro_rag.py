import time
import json
from contextlib import contextmanager
from datetime import datetime, timezone
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from rag_indexer import cargar_vectorstore, formatear_contexto

load_dotenv()

#Plantilla que me obligue a usar SOLO el contexto recuperado y también a citar [1], [2]
PROMT_TEMPLATE = """REsponde la pregunta usando SOLO el contexto de abajo. Cita la \
fuente de cada afirmacion con su numero entre corchetes, como [1]. Si el contexto no \
alcanza para responder, dilo explicitamente en vez de inventar.

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:

""" #contexto = el resultado de la busqueda de vs, formateado con formatear_contexto, pregunta = la consulta del usuario final

def aprox_tokens(texto: str) -> int:
    return len(texto) // 4

#Latencia
@contextmanager #Administrador de contexto
def medir(tiempos: dict, etapa: str):
    """
    Cronometrar bloques de código (sin "ensuciar" la lógica)
    Uso:
        with medir(tiempos, "nombre_etapa"): #ej: "embedding_y_consulta"
    """
    #1.- ANTES del bloque with
    inicio = time.perf_counter() #empiezo a contar el tiempo

    #2.- PAUSA (yield): le cede el control al código que puse en el bloque de código dentro del with
    yield

    #3.- DESPUÉS del bloque with: cuando el código termina, vuelvo aquí y detengo el tiempo
    tiempos[etapa] = time.perf_counter() - inicio #Tiempo total en el que se ejecutó esa etapa/tarea

#Calculo de costos (tokens_entrada, tokens_salida, tarifa_entrada, tarifa_salida)
def calcular_costos(tokens_entrada: int, tokens_salida: int, tarifa_entrada_x1M: float = .3, tarifa_salida_1M: float = 2.5) -> float:
    """
    Calcula el costo monetario real de la consulta con contexto de mi RAG
    """
    costo_entrada = (tokens_entrada / 1000000) * tarifa_entrada_x1M
    costo_salida = (tokens_salida / 1000000) * tarifa_salida_1M

    return round(costo_entrada + costo_salida, 6)

#Registrar consulta
def registrar_consulta(vectorstore, pregunta: str, k: int = 3) -> dict:
    """
    Ejecutar de punta a punta el proceso completo con RAG. (Recuperación + Prompt con contexto + Generación con Gemini),
    Medir la latencia de cada etapa y extraer los tokens consumidos (reales) y el costo de esto
    """
    tiempos = {} #Es donde voy a almacenar la latencia de cada etapa

    chat_model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

    #Etapa 1: Embed y la busqueda vectorial (Consulta a mi VS)
    with medir(tiempos, "embed_y_busqueda"):
        retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        chunks = retriever.invoke(pregunta)

    #Etapa 2: Armado del prompt (agregando el contexto/chunks formateados)
    with medir(tiempos, "armado_prompt"):
        contexto, citas = formatear_contexto(chunks)
        prompt = PROMT_TEMPLATE.format(contexto=contexto, pregunta=pregunta)
        
    #Etapa 3: Generación de la respuesta con Gemini
    with medir(tiempos, "generacion"):
        respuesta = chat_model.invoke(prompt)

    #respuesta tiene usage_metadata -> tokens se gastaron.
    #respuesta["usage_metadata"]["input_tokens"], respuesta["usage_metadata"]["output_tokens"]
    tokens_reales = dict(respuesta.usage_metadata) if respuesta.usage_metadata else None

    costo_usd = None

    if tokens_reales:
        costo_usd = calcular_costos(
            tokens_entrada=tokens_reales.get("input_tokens", 0),
            tokens_salida= tokens_reales.get("output_tokens", 0), #output_tokens YA INCLUYE tokens de razonamiento
            tarifa_entrada_x1M= .3,
            tarifa_salida_1M= 2.5
        )

    #Factor de crecimiento: comparación de cuánto creció el texto de entrada vs la pregunta solita
    factor_crecimiento = round(len(prompt) / len(pregunta), 1)

    #Construir el diccionario con toda la info que obtuvimos
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pregunta": pregunta,
        "k": k,
        "respuesta_generada": respuesta.content,
        "citas_disponibles": citas,
        "tiempo_ms": {etapa: round(seg * 1000, 2) for etapa, seg in tiempos.items()},
        "tiempo_total_ms": round(sum(tiempos.values()) * 1000, 2),
        "factor_crecimiento": f"{factor_crecimiento}x",
        "tokens": tokens_reales,
        "costo_estimado_usd": f"{costo_usd:.6f}"
    }

    return registro

if __name__ == "__main__":
    CARPETA_DB = "vectorstore_ejemplo"
    K = 3
    vs = cargar_vectorstore(CARPETA_DB)

    pregunta = "¿Cuántos intentos hace el cliente ante un TimeoutError y cuánto espera entre cada uno?"

    # tiempos = {}
    # with medir(tiempos, "embed_y_busqueda"):
    #     retriever = vs.as_retriever(search_kwargs={"k": K})
    #     chunks = retriever.invoke(pregunta)

    # contexto, citas = formatear_contexto(chunks)
    # prompt_con_rag = PROMT_TEMPLATE.format(contexto=contexto, pregunta=pregunta) #Prompt con los chunks que recibimos de vs y la pregunta

    # print(f"Pregunta sola. Caracteres: {len(pregunta)}. Tokens Aprox: {aprox_tokens(pregunta)}")
    # print(f"Prompt con RAG. Caracteres: {len(prompt_con_rag)}. Tokens Aprox: {aprox_tokens(prompt_con_rag)}")
    # print("Factor de crecimiento: ", round(len(prompt_con_rag) / len(pregunta), 1), "x")
    # print("Tiempos:", tiempos)

    registro = registrar_consulta(vs, pregunta, K)
    print(registro)