import json
from collections import Counter
from pathlib import Path

from .cliente import consultar_modelo
from .pipeline_limpieza import procesar_texto


CASOS = [
    {
        "id": "rhythmmentor_01_instrumento",
        "consulta": (
            "Soy principiante y practico batería electrónica. "
            "¿Qué instrumento debo registrar?"
        ),
        "referencia": "Batería electrónica.",
    },
    {
        "id": "rhythmmentor_02_nivel",
        "consulta": (
            "Mi nivel es principiante y estoy empezando a practicar batería. "
            "¿Qué nivel debes registrar?"
        ),
        "referencia": "Principiante.",
    },
    {
        "id": "rhythmmentor_03_duracion_real",
        "consulta": (
            "Practiqué durante 8 minutos. ¿Cuál fue la duración real "
            "de mi práctica?"
        ),
        "referencia": "La duración real fue de 8 minutos.",
    },
    {
        "id": "rhythmmentor_04_tempo",
        "consulta": (
            "Practiqué con el metrónomo a 60 BPM. ¿Qué tempo utilicé?"
        ),
        "referencia": "El tempo utilizado fue de 60 BPM.",
    },
    {
        "id": "rhythmmentor_05_objetivo",
        "consulta": (
            "Quiero practicar coordinación entre manos y pies. "
            "¿Cuál es mi objetivo?"
        ),
        "referencia": "Mejorar la coordinación entre manos y pies.",
    },
    {
        "id": "rhythmmentor_06_dificultad_pie",
        "consulta": (
            "Al tocar, me adelanté al usar el pie izquierdo. "
            "¿Qué dificultad reporté?"
        ),
        "referencia": "Me adelanté al usar el pie izquierdo.",
    },
    {
        "id": "rhythmmentor_07_sesion_completada",
        "consulta": (
            "Terminé el ejercicio de coordinación. "
            "¿Debo registrar la sesión como completada?"
        ),
        "referencia": "Sí, la sesión se completó.",
    },
    {
        "id": "rhythmmentor_08_sin_molestias",
        "consulta": (
            "Terminé la práctica y no sentí dolor ni molestias. "
            "¿Reporté alguna molestia?"
        ),
        "referencia": "No, no reporté dolor ni molestias.",
    },
    {
        "id": "rhythmmentor_09_duracion_sesion",
        "consulta": (
            "Tengo 20 minutos disponibles para una sesión. "
            "¿Cuánto debe durar en total?"
        ),
        "referencia": "La sesión debe durar exactamente 20 minutos.",
    },
    {
        "id": "rhythmmentor_10_suma_ejercicios",
        "consulta": (
            "Diseña tres ejercicios para una práctica de 12 minutos. "
            "¿Cuánto deben sumar sus duraciones?"
        ),
        "referencia": "Las duraciones de los tres ejercicios deben sumar 12 minutos.",
    },
    {
        "id": "rhythmmentor_11_tempo_inicial",
        "consulta": (
            "Soy principiante y mi tempo inicial es 60 BPM. "
            "¿A qué tempo comienza la práctica?"
        ),
        "referencia": "La práctica comienza a 60 BPM.",
    },
    {
        "id": "rhythmmentor_12_progresion_gradual",
        "consulta": (
            "¿Cómo debería aumentar la dificultad de mis ejercicios "
            "de batería?"
        ),
        "referencia": "Aumenta la dificultad de forma gradual.",
    },
    {
        "id": "rhythmmentor_13_historial_hi_hat",
        "consulta": (
            "En mis últimas sesiones pude mantener el hi-hat con la mano "
            "derecha. ¿Qué logré mantener?"
        ),
        "referencia": "Mantuve el hi-hat con la mano derecha.",
    },
    {
        "id": "rhythmmentor_14_historial_pie_izquierdo",
        "consulta": (
            "En la última práctica me adelanté al coordinar el bombo "
            "con el pie izquierdo. ¿Qué debo trabajar?"
        ),
        "referencia": "Debo trabajar la coordinación del bombo con el pie izquierdo.",
    },
    {
        "id": "rhythmmentor_15_registro_bateria_electronica",
        "consulta": (
            "Registra esta práctica: usé una batería electrónica "
            "durante 8 minutos."
        ),
        "referencia": "Instrumento: batería electrónica. Duración: 8 minutos.",
    },
    {
        "id": "rhythmmentor_16_registro_tempo_y_nivel",
        "consulta": (
            "Registra mi sesión: soy principiante y practiqué a 60 BPM."
        ),
        "referencia": "Nivel: principiante. Tempo: 60 BPM.",
    },
    {
        "id": "rhythmmentor_17_no_inferir_duracion",
        "consulta": (
            "Practiqué coordinación en batería, pero no recuerdo "
            "cuántos minutos. ¿Qué duración real debes registrar?"
        ),
        "referencia": "No se indicó la duración real.",
    },
    {
        "id": "rhythmmentor_18_molestia_explicita",
        "consulta": (
            "Durante la práctica sentí dolor en la muñeca. "
            "¿Debo registrar que reporté una molestia?"
        ),
        "referencia": "Sí, se reportó una molestia.",
    },
    {
        "id": "rhythmmentor_19_no_aumento_bruso",
        "consulta": (
            "Me cuesta coordinar el pie izquierdo. "
            "¿Debería duplicar de inmediato el tempo de 60 a 120 BPM?"
        ),
        "referencia": "No; la dificultad y el tempo deben aumentar gradualmente.",
    },
    {
        "id": "rhythmmentor_20_no_inferir_completado",
        "consulta": (
            "Registré una práctica, pero no dije si terminé el ejercicio. "
            "¿Debes marcarla como completada?"
        ),
        "referencia": "No; solo se marca completada si la persona confirma que terminó.",
    },
]

INSTRUCCION_SISTEMA = (
    "Eres RhythmMentor, un asistente de práctica de batería electrónica "
    "para principiantes. Responde brevemente en español y contesta lo "
    "preguntado usando los datos explícitos del caso. No inventes datos. "
    "Respeta las duraciones y los BPM indicados, recomienda progresiones "
    "graduales y no infieras molestias si no se reportan explícitamente."
)


def contar_coincidencias(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> int:
    """Cuenta las coincidencias, considerando cuántas veces aparece cada token."""
    conteo_referencia = Counter(tokens_referencia)
    conteo_respuesta = Counter(tokens_respuesta)
    return sum((conteo_referencia & conteo_respuesta).values())


def calcular_precision_cobertura_f1(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> dict[str, float]:
    """Calcula precisión, cobertura y F1 a partir de dos listas de tokens."""
    if not tokens_referencia or not tokens_respuesta:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    coincidencias = contar_coincidencias(
        tokens_referencia,
        tokens_respuesta,
    )

    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)

    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * cobertura / (precision + cobertura)

    return {
        "precision": precision,
        "cobertura": cobertura,
        "f1": f1,
    }


def calcular_metricas(
    texto_referencia: str,
    texto_respuesta: str,
) -> dict[str, float]:
    tokens_referencia = procesar_texto(texto_referencia)
    tokens_respuesta = procesar_texto(texto_respuesta)

    return calcular_precision_cobertura_f1(
        tokens_referencia,
        tokens_respuesta,
    )


def resumir_metricas(resultados: list[dict]) -> dict[str, float]:
    """Calcula los promedios de precisión, cobertura y F1."""
    if not resultados:
        return {
            "precision_promedio": 0.0,
            "cobertura_promedio": 0.0,
            "f1_promedio": 0.0,
        }

    cantidad = len(resultados)

    return {
        "precision_promedio": sum(
            resultado["precision"] for resultado in resultados
        ) / cantidad,
        "cobertura_promedio": sum(
            resultado["cobertura"] for resultado in resultados
        ) / cantidad,
        "f1_promedio": sum(
            resultado["f1"] for resultado in resultados
        ) / cantidad,
    }


def guardar_resultados(
    resultados: list[dict],
    ruta_resultados: Path,
) -> None:
    """Guarda los resultados de forma atómica para conservar el avance."""
    ruta_temporal = ruta_resultados.with_suffix(
        ruta_resultados.suffix + ".tmp"
    )

    with ruta_temporal.open("w", encoding="utf-8") as archivo:
        json.dump(
            resultados,
            archivo,
            indent=2,
            ensure_ascii=False,
        )
        archivo.flush()

    ruta_temporal.replace(ruta_resultados)


def cargar_resultados(
    ruta_resultados: Path,
    casos: list[dict],
) -> tuple[list[dict], bool]:
    """Carga resultados previos y añade IDs a registros antiguos compatibles."""
    if not ruta_resultados.exists():
        return [], False

    with ruta_resultados.open("r", encoding="utf-8-sig") as archivo:
        guardados = json.load(archivo)

    if not isinstance(guardados, list):
        raise ValueError(
            "El archivo de resultados debe contener una lista JSON."
        )

    por_id = {caso["id"]: caso for caso in casos}
    por_consulta_referencia = {
        (caso["consulta"], caso["referencia"]): caso
        for caso in casos
    }

    resultados = []
    ids_vistos = set()
    migrado = False

    for resultado in guardados:
        if not isinstance(resultado, dict):
            raise ValueError(
                "El archivo contiene un resultado que no es un objeto JSON."
            )

        caso = None

        if "id" in resultado:
            candidato = por_id.get(resultado["id"])
            if (
                candidato is not None
                and resultado.get("consulta") == candidato["consulta"]
                and resultado.get("referencia") == candidato["referencia"]
            ):
                caso = candidato
        else:
            caso = por_consulta_referencia.get(
                (
                    resultado.get("consulta"),
                    resultado.get("referencia"),
                )
            )

        if caso is None:
            raise ValueError(
                "El archivo contiene resultados de otros casos o de otra "
                "evaluación. Archívalo antes de cambiar la lista CASOS."
            )

        if caso["id"] in ids_vistos:
            raise ValueError(
                f"El caso {caso['id']} aparece duplicado en los resultados."
            )

        resultado_normalizado = {
            **resultado,
            "id": caso["id"],
            "consulta": caso["consulta"],
            "referencia": caso["referencia"],
        }
        if "id" not in resultado:
            migrado = True

        resultados.append(resultado_normalizado)
        ids_vistos.add(caso["id"])

    return resultados, migrado


def ejecutar_evaluacion() -> list[dict]:
    ruta_resultados = (
        Path(__file__).resolve().parent.parent
        / "docs"
        / "resultados_metricas.json"
    )
    ruta_resultados.parent.mkdir(parents=True, exist_ok=True)

    resultados, migrado = cargar_resultados(ruta_resultados, CASOS)

    if migrado:
        guardar_resultados(resultados, ruta_resultados)
        print("Se agregaron IDs a resultados guardados anteriormente.")

    ids_completados = {
        resultado["id"]
        for resultado in resultados
    }

    for numero, caso in enumerate(CASOS, start=1):
        if caso["id"] in ids_completados:
            print(f"Ya guardado {numero}/{len(CASOS)}: {caso['consulta']}")
            continue

        print(f"\nGenerando caso {numero}/{len(CASOS)}: {caso['consulta']}")

        try:
            respuesta = consultar_modelo(
                caso["consulta"],
                system_instruction=INSTRUCCION_SISTEMA,
            )
        except (RuntimeError, ValueError, TimeoutError) as error:
            print("Se detuvo la generación:", error)
            print(f"Respuestas conservadas: {len(resultados)}")
            break

        metricas = calcular_metricas(
            caso["referencia"],
            respuesta,
        )

        resultado = {
            "id": caso["id"],
            "consulta": caso["consulta"],
            "referencia": caso["referencia"],
            "respuesta": respuesta,
            **metricas,
        }

        resultados.append(resultado)
        ids_completados.add(caso["id"])

        # Se guarda después de cada llamada exitosa para poder reanudar.
        guardar_resultados(resultados, ruta_resultados)

        print("Respuesta:", respuesta)
        print("Métricas:", metricas)
        print(f"Guardadas: {len(resultados)}/{len(CASOS)}")

    orden_casos = {
        caso["id"]: numero
        for numero, caso in enumerate(CASOS)
    }
    resultados.sort(key=lambda resultado: orden_casos[resultado["id"]])

    if resultados:
        guardar_resultados(resultados, ruta_resultados)

    print("\nPromedios:", resumir_metricas(resultados))
    print("Resultados guardados en:", ruta_resultados)

    return resultados


if __name__ == "__main__":
    ejecutar_evaluacion()
