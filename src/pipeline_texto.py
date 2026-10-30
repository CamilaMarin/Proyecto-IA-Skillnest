from .cliente import consultar_modelo
from .pipeline_limpieza import procesar_texto


def calcular_coincidencia(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> float:
    """Calcula qué proporción de tokens distintos de la referencia coincide."""
    referencia = set(tokens_referencia)

    if not referencia:
        return 0.0

    respuesta = set(tokens_respuesta)
    return len(referencia & respuesta) / len(referencia)


def main() -> None:
    consulta = "¿Qué es Python?"
    referencia = "Python es un lenguaje de programación interpretado."
    respuesta = consultar_modelo(consulta)

    coincidencia_cruda = calcular_coincidencia(
        referencia.split(),
        respuesta.split(),
    )

    coincidencia_procesada = calcular_coincidencia(
        procesar_texto(referencia),
        procesar_texto(respuesta),
    )

    print(f"[Caso 1] Coincidencia texto crudo: {coincidencia_cruda:.1%}")
    print(
        "[Caso 1] Coincidencia texto procesado: "
        f"{coincidencia_procesada:.1%}"
    )


if __name__ == "__main__":
    main()