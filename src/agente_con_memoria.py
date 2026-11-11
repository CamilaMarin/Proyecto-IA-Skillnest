from datetime import datetime, timezone
import json

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory

from .herramientas_rhythmmentor import (
    distribuir_duracion_sesion,
    guardar_sesion_practica,
)


HERRAMIENTAS = [distribuir_duracion_sesion, guardar_sesion_practica]
HISTORIALES = {}


def obtener_historial(session_id: str) -> InMemoryChatMessageHistory:
    """Obtiene o crea el historial asociado a una sesión."""

    if session_id not in HISTORIALES:
        HISTORIALES[session_id] = InMemoryChatMessageHistory()

    return HISTORIALES[session_id]


def construir_agente_con_memoria(modelo):
    """Construye el agente y conecta su historial por session_id."""

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres RhythmMentor, un asistente para personas principiantes que practican batería electrónica. "
                "Usa el historial de esta sesión para entender referencias como 'ese tiempo' o 'mi objetivo'. No mezcles información entre sesiones y no inventes datos que la persona no haya compartido. "
                "Cuando la persona solicite repartir la duración de una sesión, el tiempo total debe estar indicado por ella. Si falta, pregunta antes de calcular. Si indicó la cantidad de ejercicios, respétala. Si no la indicó, puedes elegir una cantidad adecuada para el objetivo y el tiempo disponibles; deja claro que es tu propuesta. Usa distribuir_duracion_sesion con el tiempo total y la cantidad elegida. "
                "Usa guardar_sesion_practica únicamente si la persona pide explícitamente guardar o registrar la sesión. La herramienta presenta los datos y solicita aprobación antes de escribir; si la persona rechaza o vence el timeout, no afirmes que se guardó.",
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{entrada}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agente = create_tool_calling_agent(
        modelo,
        HERRAMIENTAS,
        prompt,
    )

    ejecutor = AgentExecutor(
        agent=agente,
        tools=HERRAMIENTAS,
        verbose=True,
        return_intermediate_steps=True,
    )

    cadena = ejecutor | RunnableLambda(limpiar_salida)

    return RunnableWithMessageHistory(
        cadena,
        obtener_historial,
        input_messages_key="entrada",
        history_messages_key="chat_history",
        output_messages_key="output",
    )


def limpiar_salida(datos: dict) -> dict:
    """Normaliza la salida si el proveedor la devuelve como bloques de texto."""

    salida = datos.get("output", "")

    if isinstance(salida, list):
        partes = []

        for parte in salida:
            if isinstance(parte, dict):
                texto = parte.get("text")
            else:
                texto = getattr(parte, "text", None)

            if texto:
                partes.append(texto)

        salida = "\n".join(partes)

    return {**datos, "output": salida}


def registrar_traza(
    session_id: str,
    entrada: str,
    resultado: dict,
) -> None:
    """Añade una interacción del agente al archivo JSONL de trazas."""

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "entrada": entrada,
        "acciones": [
            {
                "herramienta": accion.tool,
                "argumentos": accion.tool_input,
                "observacion": observacion,
            }
            for accion, observacion in resultado.get("intermediate_steps", [])
        ],
        "respuesta_final": resultado.get("output", ""),
    }

    with open("trazas_agente.jsonl", "a", encoding="utf-8") as archivo:
        archivo.write(
            json.dumps(registro, ensure_ascii=False, default=str) + "\n"
        )


if __name__ == "__main__":
    load_dotenv()

    modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    agente = construir_agente_con_memoria(modelo)

    session_id = "demo_rhythmmentor_01"
    config = {"configurable": {"session_id": session_id}}

    entradas = [
        "Soy principiante, quiero mejorar la coordinación entre manos y pies, y tengo 10 minutos para practicar.",
        "¿Cómo repartirías ese tiempo entre tres ejercicios?",
        "Completa una sesión para principiante de 10 minutos, con tres ejercicios para mejorar la coordinación entre manos y pies y tempo inicial de 60 BPM. Quiero guardar esa sesión."
    ]

    for entrada in entradas:
        resultado = agente.invoke(
            {"entrada": entrada},
            config=config,
        )

        registrar_traza(
            session_id=session_id,
            entrada=entrada,
            resultado=resultado,
        )

        print("Respuesta:", resultado["output"])
