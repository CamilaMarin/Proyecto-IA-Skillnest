from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI #Modelo
from langchain_core.prompts import PromptTemplate #Plantilla -> Prompt dinámico
from langchain_core.output_parsers import StrOutputParser #Parsea la respuesta y la transforma en solo textos
from langchain_core.runnables import (RunnableBranch, RunnablePassthrough, RunnableLambda) #Bifurcaciones/Branches/Ramificaciones

import logging #Generar un archivo de log con los errores que se presenten

from .cadena_tres_pasos import construir_cadena as construir_cadena_sesion

logger = logging.getLogger(__name__)

INTENCIONES_VALIDAS = {
    "crear_sesion",
    "proponer_ejercicio",
    "ajustar_dificultad",
    "consulta_general",
}

def normalizar_intencion(texto):
    """Normaliza la etiqueta de intención o usa la ruta general por defecto."""
    if not isinstance(texto, str):
        return "consulta_general"
    
    etiqueta = texto.strip().lower().strip(" \t\r\n`'\".,:;!")

    if etiqueta in INTENCIONES_VALIDAS:
        return etiqueta

    return "consulta_general"

def respuesta_fallback_sesion(entrada):
    """Devuelve una respuesta segura si falla la creación de la sesión."""
    error = entrada.get("error")

    if error is not None:
        logger.warning(
            "Falló la ruta para crear una sesión (%s): %s",
            type(error).__name__,
            error,
        )
    else:
        logger.warning("Falló la ruta para crear una sesión.")

    return (
        "No pude preparar tu sesión ahora. Conserva el tempo que estás practicando y vuelve a intentarlo más tarde."
    )

def construir_ruta_sesion_segura(cadena_sesion):
    """Protege la ruta de creación de sesión con una respuesta de respaldo."""
    return cadena_sesion.with_fallbacks(
        [RunnableLambda(respuesta_fallback_sesion)],
        exception_key="error",
    )

def construir_cadena_con_enrutamiento(modelo, clasificador=None):
    """Construye el clasificador y las rutas de RhythmMentor.`clasificador` se puede inyectar en las pruebas para evitar llamadas reales de clasificación a Gemini.
    """
    if clasificador is None:
        plantilla_clasificacion = PromptTemplate.from_template(
            "Clasifica la solicitud según la intención principal. "
            "Devuelve exactamente una de estas etiquetas, sin explicación:\n"
            "- crear_sesion: la persona pide una sesión de práctica.\n"
            "- proponer_ejercicio: pide un ejercicio concreto.\n"
            "- ajustar_dificultad: cuenta cómo practicó y pide ajustar "
            "el tempo o la dificultad.\n"
            "- consulta_general: hace otra consulta sobre batería o práctica, "
            "o su intención no está clara.\n\n"
            "Solicitud:\n{mensaje}"
        )

        clasificador = (
            plantilla_clasificacion
            | modelo
            | StrOutputParser()
        )

    paso_clasificacion = (
        clasificador
        | RunnableLambda(normalizar_intencion)
    )

    cadena_sesion = construir_cadena_sesion(modelo)

    adaptar_solicitud_a_sesion = RunnableLambda(
        lambda datos: {"solicitud": datos["mensaje"]}
    )

    ruta_crear_sesion = construir_ruta_sesion_segura(
        adaptar_solicitud_a_sesion | cadena_sesion
    )

    ruta_proponer_ejercicio = (
        PromptTemplate.from_template(
            "Eres RhythmMentor, un asistente de práctica de batería "
            "electrónica. Propón un ejercicio concreto y progresivo "
            "apropiado para el nivel y objetivo que indique la persona. "
            "Incluye instrucciones claras y un criterio sencillo para "
            "evaluar la práctica. No inventes datos que no haya indicado.\n\n"
            "Solicitud:\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )

    ruta_ajustar_dificultad = (
        PromptTemplate.from_template(
            "Eres RhythmMentor, un asistente de práctica de batería "
            "electrónica. Usa el desempeño que describe la persona para "
            "sugerir un ajuste gradual de tempo o complejidad. Explica "
            "brevemente el motivo y no recomiendes aumentos bruscos. "
            "Si falta información necesaria, pide una aclaración.\n\n"
            "Solicitud:\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )

    ruta_consulta_general = (
        PromptTemplate.from_template(
            "Eres RhythmMentor, un asistente para personas que practican "
            "batería electrónica, especialmente principiantes. Responde "
            "de forma clara y segura a la consulta. Si no queda claro qué "
            "necesita la persona, haz una pregunta de aclaración.\n\n"
            "Consulta:\n{mensaje}"
        )
        | modelo
        | StrOutputParser()
    )

    bifurcacion = RunnableBranch(
        (
            lambda datos: datos["clasificacion"] == "crear_sesion",
            ruta_crear_sesion,
        ),
        (
            lambda datos: datos["clasificacion"] == "proponer_ejercicio",
            ruta_proponer_ejercicio,
        ),
        (
            lambda datos: datos["clasificacion"] == "ajustar_dificultad",
            ruta_ajustar_dificultad,
        ),
        ruta_consulta_general,
    )

    return (
        RunnablePassthrough.assign(clasificacion=paso_clasificacion)
        | bifurcacion
    )

def procesar_mensaje_seguro(cadena, mensaje):
    """Ejecuta el flujo y evita que una excepción llegue sin manejar."""

    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception as error:
        logger.error(
            "Error procesando el mensaje de RhythmMentor: (%s): %s",
            type(error).__name__,
            error,
        )
        return (
            "No pudimos procesar tu solicitud en este momento. Intenta de nuevo más tarde."
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", #2026-11-04 19:40 [WARNING] main: No se puede ejecutar x
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="error.log",
        filemode="a",
        encoding="utf-8",
        force=True
    )

    load_dotenv()

    modelo = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    cadena = construir_cadena_con_enrutamiento(modelo)

    mensaje = (
        "Soy principiante en batería electrónica. Tengo 20 minutos y quiero "
        "mejorar la coordinación entre manos y pies. Mi tempo inicial es 60 BPM."
    )

    print(procesar_mensaje_seguro(cadena, mensaje))