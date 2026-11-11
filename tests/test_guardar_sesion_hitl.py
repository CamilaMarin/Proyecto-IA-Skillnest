import pytest

import src.herramientas_rhythmmentor as herramientas
from src.repositorio_sesiones import RepositorioSesiones


def datos_sesion():
    return {
        "nivel": "principiante",
        "objetivo": "Mejorar la coordinación entre manos y pies",
        "duracion_total_minutos": 10,
        "tempo_inicial_bpm": 60,
        "ejercicios": [
            {
                "nombre": "Manos alternas",
                "instrucciones": "Alternar golpes de derecha e izquierda.",
                "duracion_minutos": 5,
                "tempo_bpm": 60,
            },
            {
                "nombre": "Coordinación con bombo",
                "instrucciones": "Mantener un pulso constante con el bombo.",
                "duracion_minutos": 5,
                "tempo_bpm": 60,
            },
        ],
    }


@pytest.fixture
def repositorio_temporal(tmp_path, monkeypatch):
    repositorio = RepositorioSesiones(tmp_path / "sesiones_test.db")
    monkeypatch.setattr(
        herramientas,
        "RepositorioSesiones",
        lambda: repositorio,
    )
    return repositorio


def test_guarda_solo_despues_de_aprobacion(
    repositorio_temporal,
    monkeypatch,
):
    monkeypatch.setattr(
        herramientas,
        "esperar_aprobacion",
        lambda mensaje, timeout_segundos: True,
    )

    resultado = herramientas.guardar_sesion_practica.invoke(datos_sesion())

    assert "Sesión guardada" in resultado
    sesiones = repositorio_temporal.listar_sesiones()
    assert len(sesiones) == 1
    assert sesiones[0]["duracion_total_minutos"] == 10


def test_no_guarda_si_no_hay_aprobacion(
    repositorio_temporal,
    monkeypatch,
):
    monkeypatch.setattr(
        herramientas,
        "esperar_aprobacion",
        lambda mensaje, timeout_segundos: False,
    )

    resultado = herramientas.guardar_sesion_practica.invoke(datos_sesion())

    assert "no se aprobó o venció" in resultado
    assert repositorio_temporal.ruta_db.exists() is False


def test_esperar_aprobacion_deniega_cuando_vence_timeout(monkeypatch):
    class EntradaSinRespuesta:
        @staticmethod
        def isatty():
            return True

        @staticmethod
        def readline():
            pytest.fail("No debería leer una respuesta si venció el timeout.")

    class SistemaPosix:
        name = "posix"

    monkeypatch.setattr(herramientas, "os", SistemaPosix)
    monkeypatch.setattr(herramientas.sys, "stdin", EntradaSinRespuesta())
    monkeypatch.setattr(
        herramientas.select,
        "select",
        lambda lectores, escritores, excepciones, timeout: ([], [], []),
    )

    assert herramientas.esperar_aprobacion("Confirmar guardado", 15) is False


def test_no_pide_aprobacion_si_las_duraciones_no_suman_el_total(
    repositorio_temporal,
    monkeypatch,
):
    def fallo_si_pide_aprobacion(*args, **kwargs):
        pytest.fail("No debe pedir aprobación para un plan inválido.")

    monkeypatch.setattr(
        herramientas,
        "esperar_aprobacion",
        fallo_si_pide_aprobacion,
    )
    datos = datos_sesion()
    datos["ejercicios"][0]["duracion_minutos"] = 4

    resultado = herramientas.guardar_sesion_practica.invoke(datos)

    assert "no coincide con el tiempo total" in resultado
    assert repositorio_temporal.ruta_db.exists() is False
