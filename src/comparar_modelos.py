import time
import statistics

from consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    calcular_costos,
)

MODELOS = [
    {
        "nombre": "gemini-3.6-flash",
        "precio_entrada": 0.00000075,
        "precio_salida": 0.00000375,
    },
    {
        "nombre": "gemini-3.5-flash-lite",
        "precio_entrada": 0.0000003,
        "precio_salida": 0.0000025,
    },
    {
        "nombre": "gemini-3.1-flash-lite",
        "precio_entrada": 0.00000025,
        "precio_salida": 0.0000015,
    },
]

# Reemplazar nombres y tarifas con valores reales.
# Los ceros anteriores son marcadores, no precios verificados.

REPETICIONES = 4

PROMPT = (
    "Soy principiante en batería electrónica. "
    "Tengo 20 minutos disponibles y quiero mejorar "
    "la coordinación entre manos y pies. "
    "Mi tempo inicial es 60 BPM. "
    "Genera una sesión estructurada con ejercicios, "
    "duración, instrucciones y objetivos. "
    "La duración total debe ser exactamente 20 minutos."
)


def probar_modelo(configuracion):
    nombre = configuracion["nombre"]
    resultados = []

    print(f"\n{'=' * 60}")
    print(f"PROBANDO MODELO: {nombre}")
    print(f"{'=' * 60}")

    for numero in range(1, REPETICIONES + 1):
        print(f"\nEjecución {numero}/{REPETICIONES}")

        url, body = armar_peticion(PROMPT, nombre)

        inicio = time.perf_counter()

        try:
            datos = enviar_peticion(url, body)
            latencia = time.perf_counter() - inicio

            respuesta = extraer_texto(datos)

            costo = calcular_costos(
                datos,
                configuracion["precio_entrada"],
                configuracion["precio_salida"],
            )

            resultados.append({
                "latencia": latencia,
                "costo": costo,
                "respuesta": respuesta,
            })

            print(f"Latencia: {latencia:.2f} segundos")
            print(f"Costo estimado: ${costo:.8f} USD")
            print(f"Respuesta:\n{respuesta}")

        except RuntimeError as error:
            print(f"Error en la ejecución: {error}")

    return resultados


def main():
    resumen = []

    for modelo in MODELOS:
        resultados = probar_modelo(modelo)

        if not resultados:
            print(f"Sin resultados válidos para {modelo['nombre']}")
            continue

        latencia_promedio = statistics.mean(
            resultado["latencia"]
            for resultado in resultados
        )

        costo_promedio = statistics.mean(
            resultado["costo"]
            for resultado in resultados
        )

        resumen.append({
            "modelo": modelo["nombre"],
            "latencia": latencia_promedio,
            "costo": costo_promedio,
            "exitosas": len(resultados),
        })

    print("\n\nTABLA COMPARATIVA")
    print(
        f"{'Modelo':<25}"
        f"{'Latencia promedio':<22}"
        f"{'Costo promedio':<20}"
        f"{'Éxitos'}"
    )

    for item in resumen:
        print(
            f"{item['modelo']:<25}"
            f"{item['latencia']:<22.2f}"
            f"${item['costo']:<19.8f}"
            f"{item['exitosas']}/{REPETICIONES}"
        )


if __name__ == "__main__":
    main()