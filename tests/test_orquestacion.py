import logging

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from src.enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_ruta_sesion_segura,
    normalizar_intencion,
    procesar_mensaje_seguro,
)


def crear_modelo_falso(respuestas):
    """Crea un modelo simulado que devuelve respuestas en orden."""

    prompts_recibidos = []
    respuestas_pendientes = iter(respuestas)

    def responder(prompt):
        prompts_recibidos.append(prompt.to_string())
        return AIMessage(content=next(respuestas_pendientes))

    return RunnableLambda(responder), prompts_recibidos


def test_normalizar_intencion_limpia_mayusculas_y_espacios():
    assert normalizar_intencion(" AJUSTAR_DIFICULTAD \n") == (
        "ajustar_dificultad"
    )


def test_normalizar_intencion_desconocida_usa_consulta_general():
    assert normalizar_intencion("otra_intencion") == "consulta_general"


@pytest.mark.parametrize(
    ("intencion", "respuestas", "respuesta_esperada", "llamadas_modelo"),
    [
        (
            "crear_sesion",
            [
                "Nivel: principiante; objetivo: coordinación; "
                "duración: 20 minutos; BPM: 60",
                "Plan: dos ejercicios de 10 minutos a 60 BPM.",
                "Sesión final: dos ejercicios de 10 minutos a 60 BPM.",
            ],
            "Sesión final: dos ejercicios de 10 minutos a 60 BPM.",
            3,
        ),
        (
            "proponer_ejercicio",
            ["Ejercicio: coordinación a 60 BPM."],
            "Ejercicio: coordinación a 60 BPM.",
            1,
        ),
        (
            "ajustar_dificultad",
            ["Mantén el tempo actual y trabaja la coordinación gradualmente."],
            "Mantén el tempo actual y trabaja la coordinación gradualmente.",
            1,
        ),
        (
            "intencion_desconocida",
            ["¿Quieres crear una sesión o consultar sobre un ejercicio?"],
            "¿Quieres crear una sesión o consultar sobre un ejercicio?",
            1,
        ),
    ],
)
def test_enrutamiento_selecciona_la_ruta_y_devuelve_respuesta(
    intencion,
    respuestas,
    respuesta_esperada,
    llamadas_modelo,
):
    modelo_falso, prompts_recibidos = crear_modelo_falso(respuestas)
    clasificador_falso = RunnableLambda(lambda _entrada: intencion)

    cadena = construir_cadena_con_enrutamiento(
        modelo_falso,
        clasificador=clasificador_falso,
    )

    mensaje = (
        "Soy principiante; quiero practicar coordinación durante 20 minutos "
        "a 60 BPM."
    )

    resultado = cadena.invoke({"mensaje": mensaje})

    assert resultado == respuesta_esperada
    assert len(prompts_recibidos) == llamadas_modelo


def test_ruta_de_sesion_devuelve_fallback_si_falla(caplog):
    def fallar_a_proposito(_entrada):
        raise ConnectionError("fallo simulado")

    cadena_sesion_falsa = RunnableLambda(fallar_a_proposito)
    cadena_segura = construir_ruta_sesion_segura(cadena_sesion_falsa)

    with caplog.at_level(logging.WARNING, logger="src.enrutamiento"):
        resultado = cadena_segura.invoke(
            {"mensaje": "Quiero una sesión para practicar coordinación."}
        )

    assert "No pude preparar tu sesión" in resultado
    assert "Falló la ruta para crear una sesión" in caplog.text
    assert "ConnectionError" in caplog.text
    assert "fallo simulado" in caplog.text
    assert "Traceback" not in caplog.text


def test_procesar_mensaje_seguro_atrapa_fallo_de_clasificacion(caplog):
    def fallar_clasificacion(_entrada):
        raise ConnectionError("fallo simulado en clasificación")

    clasificador_falso = RunnableLambda(fallar_clasificacion)
    modelo_falso, prompts_recibidos = crear_modelo_falso(
        ["Esta respuesta no debería usarse."]
    )

    cadena = construir_cadena_con_enrutamiento(
        modelo_falso,
        clasificador=clasificador_falso,
    )

    with caplog.at_level(logging.ERROR, logger="src.enrutamiento"):
        resultado = procesar_mensaje_seguro(
            cadena,
            "Quiero practicar batería.",
        )

    assert "No pudimos procesar tu solicitud" in resultado
    assert "fallo simulado en clasificación" in caplog.text
    assert prompts_recibidos == []