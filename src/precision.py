import json
from collections import Counter
from pathlib import Path

from .cliente import consultar_modelo
from .pipeline_limpieza import procesar_texto


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


def ejecutar_evaluacion() -> list[dict]:
    casos = [
        (
            "¿Qué es Python?",
            "Python es un lenguaje de programación interpretado.",
        ),
        (
            "¿Cuándo se creó Python?",
            "Python fue creado en 1991.",
        ),
        (
            "¿Qué es una lista en Python?",
            "Una lista es una colección ordenada y modificable.",
        ),
    ]

    resultados = []

    for consulta, referencia in casos:
        respuesta = consultar_modelo(
            consulta,
            system_instruction=(
                "Responde en español con una definición breve, en una sola "
                "oración de máximo 15 palabras. Sin listas, ejemplos ni "
                "introducciones."
            ),
        )

        metricas = calcular_metricas(referencia, respuesta)

        print("Consulta:", consulta)
        print("Respuesta:", respuesta)
        print("Métricas:", metricas)

        resultados.append({
            "consulta": consulta,
            "respuesta": respuesta,
            **metricas,
        })

    resultados.sort(key=lambda resultado: resultado["f1"])

    ruta_resultados = (
        Path(__file__).resolve().parent.parent
        / "docs"
        / "resultados_metricas.json"
    )
    ruta_resultados.parent.mkdir(parents=True, exist_ok=True)

    with ruta_resultados.open("w", encoding="utf-8") as archivo:
        json.dump(resultados, archivo, indent=2, ensure_ascii=False)

    print("Promedios:", resumir_metricas(resultados))
    print("Resultados guardados en:", ruta_resultados)

    print("Casos con menor F1:")
    for caso in resultados[:3]:
        print(caso["consulta"], caso["f1"])

    return resultados


if __name__ == "__main__":
    ejecutar_evaluacion()