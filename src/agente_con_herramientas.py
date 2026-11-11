from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

from .herramientas_rhythmmentor import distribuir_duracion_sesion


HERRAMIENTAS = [distribuir_duracion_sesion]


def construir_ejecutor(modelo):
    """Construye el agente de RhythmMentor con sus herramientas."""

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Eres RhythmMentor, un asistente para personas principiantes que practican batería electrónica. "
                "Cuando la persona solicite repartir el tiempo de una sesión, el total de minutos debe estar indicado por ella. Si falta, pregunta antes de calcular y no llames a la herramienta. "
                "Si indicó cuántos ejercicios quiere, respeta esa cantidad. "
                "Si no indicó una cantidad, puedes proponer una adecuada para el objetivo y el tiempo disponibles. Deja claro que es una decisión de tu propuesta, no un dato entregado por la persona. "
                "Usa distribuir_duracion_sesion para calcular el reparto. "
                "La herramienta calcula duraciones; tú propones el contenido musical de los ejercicios por separado.",
            ),
            ("human", "{entrada}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agente = create_tool_calling_agent(
        modelo,
        HERRAMIENTAS,
        prompt,
    )

    return AgentExecutor(
        agent=agente,
        tools=HERRAMIENTAS,
        verbose=True,
        return_intermediate_steps=True,
    )


if __name__ == "__main__":
    load_dotenv()

    modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    ejecutor = construir_ejecutor(modelo)

    resultado = ejecutor.invoke(
        {
            "entrada": (
                "Tengo 10 minutos y quiero hacer tres ejercicios "
                "de batería. ¿Cómo reparto el tiempo?"
            )
        }
    )

    print("Respuesta:", resultado["output"])