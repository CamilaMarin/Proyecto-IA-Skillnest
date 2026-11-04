from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from src.cadena_tres_pasos import construir_cadena


def test_cadena_conecta_los_tres_pasos_y_conserva_requisitos():
    prompts_recibidos = []

    requisitos_extraidos = (
        "Nivel: principiante\n"
        "Objetivo: coordinación entre manos y pies\n"
        "Duración disponible: 20 minutos\n"
        "BPM inicial: 60"
    )

    plan_propuesto = (
        "Plan preliminar: dos ejercicios de 10 minutos, "
        "ambos a 60 BPM."
    )

    respuestas = iter([
        requisitos_extraidos,
        plan_propuesto,
        "Sesión final: dos ejercicios de 10 minutos a 60 BPM.",
    ])

    def responder(prompt):
        prompts_recibidos.append(prompt.to_string())
        return AIMessage(content=next(respuestas))

    modelo_falso = RunnableLambda(responder)
    cadena = construir_cadena(modelo_falso)

    solicitud = (
        "Soy principiante en batería electrónica. Tengo 20 minutos y "
        "quiero mejorar la coordinación entre manos y pies. Mi tempo "
        "inicial es 60 BPM."
    )

    resultado = cadena.invoke({"solicitud": solicitud})

    assert len(prompts_recibidos) == 3

    # El primer paso recibe la solicitud original.
    assert solicitud in prompts_recibidos[0]

    # El segundo paso recibe los requisitos extraídos.
    assert requisitos_extraidos in prompts_recibidos[1]

    # El tercer paso recibe tanto los requisitos como el plan propuesto.
    assert requisitos_extraidos in prompts_recibidos[2]
    assert plan_propuesto in prompts_recibidos[2]

    # La cadena devuelve el texto del tercer paso.
    assert isinstance(resultado, str)
    assert resultado == "Sesión final: dos ejercicios de 10 minutos a 60 BPM."