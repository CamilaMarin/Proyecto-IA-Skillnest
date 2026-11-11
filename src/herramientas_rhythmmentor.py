import os
import select
import sqlite3
import sys
import time

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from .repositorio_sesiones import RepositorioSesiones


@tool
def distribuir_duracion_sesion(
    total_minutos: int,
    cantidad_ejercicios: int,
) -> str:
    """
    Reparte el tiempo total de una sesión entre varios ejercicios.

    Usar cuando la persona haya indicado el tiempo total. Si indicó
    la cantidad de ejercicios, usar esa cantidad. Si no la indicó,
    el agente puede proponer una cantidad adecuada al objetivo y al
    tiempo disponibles, y debe presentarla como parte de su propuesta.

    Las duraciones se expresan en minutos enteros y suman exactamente
    el total. Esta herramienta solo calcula la distribución; no decide
    qué ejercicios musicales realizar.
    """
    if type(total_minutos) is not int or type(cantidad_ejercicios) is not int:
        return "Los minutos y la cantidad de ejercicios deben ser números enteros."

    if total_minutos <= 0 or cantidad_ejercicios <= 0:
        return "Los minutos y la cantidad de ejercicios deben ser mayores que cero."

    if total_minutos < cantidad_ejercicios:
        return ("No alcanza el tiempo para asignar al menos un minuto a cada ejercicio.")

    minutos_base, minutos_sobrantes = divmod(
        total_minutos,
        cantidad_ejercicios,
    )

    duraciones = [
        minutos_base + (1 if indice < minutos_sobrantes else 0)
        for indice in range(cantidad_ejercicios)
    ]

    detalle = [
        f"Ejercicio {indice + 1}: {duracion} minuto(s)"
        for indice, duracion in enumerate(duraciones)
    ]

    return (
        "\n".join(detalle)
        + f"\nTotal: {sum(duraciones)} minuto(s)"
    )


class EjercicioSesion(BaseModel):
    """Datos persistibles de un ejercicio de práctica."""

    nombre: str = Field(min_length=1, description="Nombre breve del ejercicio.")
    instrucciones: str = Field(
        default="",
        description="Instrucciones del ejercicio.",
    )
    duracion_minutos: int = Field(
        gt=0,
        description="Duración del ejercicio en minutos enteros.",
    )
    tempo_bpm: int | None = Field(
        default=None,
        gt=0,
        description="Tempo sugerido en BPM, si fue definido.",
    )


class ArgumentosGuardarSesion(BaseModel):
    """Esquema de datos que el agente debe proponer para guardar."""

    nivel: str = Field(min_length=1, description="Nivel musical indicado.")
    objetivo: str = Field(min_length=1, description="Objetivo de la práctica.")
    duracion_total_minutos: int = Field(
        gt=0,
        description="Duración total de la sesión en minutos.",
    )
    tempo_inicial_bpm: int | None = Field(
        default=None,
        gt=0,
        description="Tempo inicial en BPM, si fue definido.",
    )
    ejercicios: list[EjercicioSesion] = Field(
        min_length=1,
        description="Ejercicios propuestos y sus duraciones.",
    )


def _esperar_aprobacion_windows(mensaje: str, timeout_segundos: int) -> bool:
    """Lee una confirmación de consola con timeout en Windows."""
    import msvcrt

    print(f"{mensaje}\nConfirma con s y Enter (límite: {timeout_segundos}s): ", end="", flush=True)
    respuesta = []
    limite = time.monotonic() + timeout_segundos

    while time.monotonic() < limite:
        if msvcrt.kbhit():
            caracter = msvcrt.getwch()
            if caracter in ("\r", "\n"):
                print()
                return "".join(respuesta).strip().lower() == "s"
            if caracter in ("\b", "\x7f"):
                if respuesta:
                    respuesta.pop()
                    print("\b \b", end="", flush=True)
            elif caracter not in ("\x00", "\xe0"):
                respuesta.append(caracter)
                print(caracter, end="", flush=True)
        time.sleep(0.05)

    print("\nTiempo agotado; no se guardó la sesión.")
    return False


def esperar_aprobacion(mensaje: str, timeout_segundos: int = 15) -> bool:
    """Espera aprobación explícita; ante no, EOF o timeout, rechaza."""
    if not sys.stdin.isatty():
        return False

    try:
        if os.name == "nt":
            return _esperar_aprobacion_windows(mensaje, timeout_segundos)

        print(
            f"{mensaje}\nConfirma con s y Enter (límite: {timeout_segundos}s): ",
            end="",
            flush=True,
        )
        disponibles, _, _ = select.select(
            [sys.stdin],
            [],
            [],
            timeout_segundos,
        )
        if not disponibles:
            print("\nTiempo agotado; no se guardó la sesión.")
            return False

        respuesta = sys.stdin.readline().strip().lower()
        return respuesta == "s"
    except (EOFError, KeyboardInterrupt, OSError, ValueError):
        print("\nNo se recibió aprobación; no se guardó la sesión.")
        return False


@tool(args_schema=ArgumentosGuardarSesion)
def guardar_sesion_practica(
    nivel: str,
    objetivo: str,
    duracion_total_minutos: int,
    ejercicios: list[EjercicioSesion],
    tempo_inicial_bpm: int | None = None,
) -> str:
    """Guarda una sesión solo cuando la persona lo pide y la aprueba.

    Usar únicamente si la persona pide explícitamente guardar o registrar
    la sesión. Antes de escribir, muestra sus datos y pide confirmación.
    Si la persona rechaza o vence el timeout, no se crea la sesión.
    """
    if sum(ejercicio.duracion_minutos for ejercicio in ejercicios) != duracion_total_minutos:
        return (
            "No guardé la sesión: la suma de las duraciones de los ejercicios "
            "no coincide con el tiempo total."
        )

    resumen = [
        "Se solicita guardar esta sesión de RhythmMentor:",
        f"Nivel: {nivel}",
        f"Objetivo: {objetivo}",
        f"Duración total: {duracion_total_minutos} minutos",
        f"Tempo inicial: {tempo_inicial_bpm if tempo_inicial_bpm is not None else 'no especificado'} BPM",
        "Ejercicios:",
    ]
    resumen.extend(
        f"- {ejercicio.nombre}: {ejercicio.duracion_minutos} min; "
        f"{ejercicio.instrucciones}"
        for ejercicio in ejercicios
    )

    if not esperar_aprobacion("\n".join(resumen), timeout_segundos=15):
        return "No guardé la sesión: no se aprobó o venció el tiempo de espera."

    try:
        sesion = RepositorioSesiones().guardar_sesion(
            nivel=nivel,
            objetivo=objetivo,
            duracion_total_minutos=duracion_total_minutos,
            tempo_inicial_bpm=tempo_inicial_bpm,
            ejercicios=[ejercicio.model_dump() for ejercicio in ejercicios],
        )
    except (ValueError, OSError, sqlite3.Error) as error:
        return f"No se pudo guardar la sesión: {error}"

    return f"Sesión guardada con el identificador {sesion['id']}."
