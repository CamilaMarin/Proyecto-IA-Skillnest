"""Chain de RhythmMentor para diseñar y revisar una sesión de práctica."""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough


def construir_cadena(modelo):
    """Construye la cadena para extraer requisitos, diseñar y revisar una sesión."""

    plantilla_requisitos = PromptTemplate.from_template(
        "Extrae de la solicitud los siguientes datos: nivel, objetivo de "
        "práctica, duración disponible en minutos y BPM inicial. "
        "Escribe 'no indicado' cuando falte un dato. No inventes información.\n\n"
        "Solicitud:\n{solicitud}"
    )

    paso_requisitos = (
        plantilla_requisitos
        | modelo
        | StrOutputParser()
    )

    plantilla_sesion = PromptTemplate.from_template(
        "Diseña una sesión de práctica de batería electrónica para una persona con el nivel indicado en los requisitos, usando los requisitos extraídos.\n"
        "Incluye ejercicios con nombre, objetivo, instrucciones, duración en "
        "minutos y BPM. La suma de las duraciones debe coincidir con el tiempo "
        "disponible. Conserva el BPM indicado; no propongas aumentos de tempo "
        "sin datos que los justifiquen. Si falta un dato esencial, indícalo "
        "y pide aclaración en vez de inventarlo.\n\n"
        "Requisitos:\n{requisitos}"
    )

    paso_sesion = (
        plantilla_sesion
        | modelo
        | StrOutputParser()
    )

    plantilla_revision = PromptTemplate.from_template(
        "Revisa la sesión propuesta comparándola con los requisitos originales.\n"
        "Comprueba que respete el nivel, el objetivo, la duración disponible y "
        "el BPM indicado. Revisa también que la suma de las duraciones de los "
        "ejercicios coincida con el tiempo disponible. Si encuentras errores, "
        "corrígelos. No agregues datos que no aparezcan en los requisitos. "
        "Devuelve únicamente la versión final de la sesión.\n\n"
        "Requisitos originales:\n{requisitos}\n\n"
        "Sesión propuesta:\n{plan}"
    )

    paso_revision = (
        plantilla_revision
        | modelo
        | StrOutputParser()
    )

    cadena = (
        RunnablePassthrough.assign(requisitos=paso_requisitos)
        | RunnablePassthrough.assign(plan=paso_sesion)
        | paso_revision
    )

    return cadena


if __name__ == "__main__":
    load_dotenv()

    modelo = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite"
    )

    cadena = construir_cadena(modelo)

    solicitud = (
        "Soy principiante en batería electrónica. Tengo 20 minutos y quiero "
        "mejorar la coordinación entre manos y pies. Mi tempo inicial es 60 BPM."
    )

    resultado = cadena.invoke({"solicitud": solicitud})
    print(resultado)