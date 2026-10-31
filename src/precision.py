import json
from collections import Counter
from pathlib import Path

from .cliente import consultar_modelo
from .pipeline_limpieza import procesar_texto


CASOS = [
    {
        "id": "python_que_es",
        "consulta": "¿Qué es Python?",
        "referencia": "Python es un lenguaje de programación interpretado.",
    },
    {
        "id": "python_fecha",
        "consulta": "¿Cuándo se creó Python?",
        "referencia": "Python fue creado en 1991.",
    },
    {
        "id": "python_lista",
        "consulta": "¿Qué es una lista en Python?",
        "referencia": "Una lista es una colección ordenada y modificable.",
    },
]

INSTRUCCION_SISTEMA = (
    "Responde en español con una definición breve, en una sola oración "
    "de máximo 15 palabras. Sin listas, ejemplos ni introducciones."
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
