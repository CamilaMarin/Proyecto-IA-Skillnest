import statistics
import time
from datetime import datetime
from pathlib import Path

from consumir_gemini import (
    armar_peticion,
    enviar_peticion,
    extraer_texto,
    calcular_costos,
)

MODELOS = [
    {
        "nombre": "gemini-3.8-flash",
        "precio_entrada": 0.00000075,
        "precio_salida": 0.00000375,
    },
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

PROMPTS = [
    {
        "nombre": "crear_sesion_coordinacion",
        "texto": (
            "Soy principiante en batería electrónica. Tengo 20 minutos disponibles "
            "y quiero mejorar la coordinación entre manos y pies. Mi tempo inicial "
            "es 60 BPM. Genera una sesión estructurada con ejercicios, duración, "
            "instrucciones y objetivos. La duración total debe ser exactamente "
            "20 minutos."
        ),
    },
    {
        "nombre": "ajustar_practica_segun_progreso",
        "texto": (
            "Soy principiante en batería electrónica y practico a 60 BPM. En mis "
            "últimas tres sesiones pude mantener el hi-hat con la mano derecha, "
            "pero me adelanté al coordinar el bombo con el pie izquierdo. Diseña "
            "una práctica de exactamente 12 minutos para trabajar ese problema. "
            "Incluye tres ejercicios con duración, BPM, instrucciones y objetivo; "
            "la suma de las duraciones debe ser exactamente 12 minutos. Aumenta "
            "la dificultad de forma gradual y agrega una recomendación para evitar "
            "tensión o dolor."
        ),
    },
]


def probar_modelo(configuracion, prompt_config):
    nombre = configuracion["nombre"]
    resultados = []

    print(f"\n{'=' * 60}")
    print(f"PROBANDO MODELO: {nombre}")
    print(f"PROMPT: {prompt_config['nombre']}")
    print(f"{'=' * 60}")

    for numero in range(1, REPETICIONES + 1):
        print(f"\nEjecución {numero}/{REPETICIONES}")
        url, body = armar_peticion(prompt_config["texto"],"Eres RhythmMentor, un asistente de práctica musical.", response_schema=None, modelo=nombre)
        inicio = time.perf_counter()

        try:
            datos = enviar_peticion(url, body)
            latencia = time.perf_counter() - inicio
            respuesta = extraer_texto(datos)
            costo, total_tokens = calcular_costos(
                datos,
                configuracion["precio_entrada"],
                configuracion["precio_salida"],
            )

            resultados.append({
                "latencia": latencia,
                "costo": costo,
                "respuesta": respuesta,
                "error": None,
            })
            print(f"Latencia: {latencia:.2f} segundos")
            print(f"Costo estimado: ${costo:.8f} USD")
            print(f"Respuesta:\n{respuesta}")

        except (RuntimeError, ValueError, TimeoutError) as error:
            resultados.append({"error": str(error)})
            print(f"Error en la ejecución: {error}")

    return resultados


def guardar_resumen(resumen, resultados_por_prueba):
    carpeta = Path(__file__).resolve().parent.parent / "docs"
    carpeta.mkdir(parents=True, exist_ok=True)

    ahora = datetime.now().astimezone()
    fecha = ahora.strftime("%Y-%m-%d_%H-%M-%S")
    momento = ahora.strftime("%Y-%m-%d %H:%M:%S %Z")
    archivo = carpeta / f"comparativa_modelos_{fecha}.md"

    lineas = [
        "# Comparativa de modelos",
        "",
        f"Fecha: {momento}",
        f"Repeticiones por modelo y prompt: {REPETICIONES}",
        "",
        "## Prompts utilizados",
        "",
    ]
    for prompt in PROMPTS:
        lineas.extend([f"### {prompt['nombre']}", "", prompt["texto"], ""])

    lineas.extend([
        "## Resultados promedio",
        "",
        "| Prompt | Modelo | Latencia promedio (s) | Costo promedio estimado (USD) | Éxitos |",
        "| --- | --- | ---: | ---: | ---: |",
    ])

    for item in resumen:
        latencia = f"{item['latencia']:.2f}" if item["latencia"] is not None else "—"
        costo = f"{item['costo']:.8f}" if item["costo"] is not None else "—"
        lineas.append(
            f"| {item['prompt']} | {item['modelo']} | {latencia} | {costo} "
            f"| {item['exitosas']}/{REPETICIONES} |"
        )

    lineas.extend(["", "## Respuestas por ejecución", ""])
    for prompt in PROMPTS:
        lineas.extend([f"### Prompt: {prompt['nombre']}", ""])
        for modelo in MODELOS:
            clave = (prompt["nombre"], modelo["nombre"])
            ejecuciones = resultados_por_prueba[clave]
            lineas.extend([f"#### {modelo['nombre']}", ""])
            for numero, resultado in enumerate(ejecuciones, start=1):
                lineas.extend([f"##### Ejecución {numero}", ""])
                if resultado.get("error"):
                    lineas.extend([f"Error: {resultado['error']}", ""])
                    continue
                lineas.extend([
                    f"- Latencia: {resultado['latencia']:.2f} s",
                    f"- Costo estimado: ${resultado['costo']:.8f} USD",
                    "",
                    "```text",
                    resultado["respuesta"].rstrip(),
                    "```",
                    "",
                ])

    archivo.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"\nResumen guardado en: {archivo}")


def main():
    resumen = []
    resultados_por_prueba = {}

    for prompt in PROMPTS:
        for modelo in MODELOS:
            resultados = probar_modelo(modelo, prompt)
            resultados_por_prueba[(prompt["nombre"], modelo["nombre"])] = resultados
            exitosos = [resultado for resultado in resultados if not resultado.get("error")]

            resumen.append({
                "prompt": prompt["nombre"],
                "modelo": modelo["nombre"],
                "latencia": statistics.mean(r["latencia"] for r in exitosos) if exitosos else None,
                "costo": statistics.mean(r["costo"] for r in exitosos) if exitosos else None,
                "exitosas": len(exitosos),
            })

    print("\n\nTABLA COMPARATIVA")
    print(f"{'Prompt':<38}{'Modelo':<28}{'Latencia prom.':<18}{'Costo prom.':<18}{'Éxitos'}")
    for item in resumen:
        latencia = f"{item['latencia']:.2f}" if item["latencia"] is not None else "—"
        costo = f"${item['costo']:.8f}" if item["costo"] is not None else "—"
        print(
            f"{item['prompt']:<38}{item['modelo']:<28}{latencia:<18}"
            f"{costo:<18}{item['exitosas']}/{REPETICIONES}"
        )

    guardar_resumen(resumen, resultados_por_prueba)


if __name__ == "__main__":
    main()
