import pytest

from src.agente_con_memoria import HISTORIALES, obtener_historial


@pytest.fixture(autouse=True)
def reiniciar_historiales():
    HISTORIALES.clear()
    yield
    HISTORIALES.clear()


def test_mismo_session_id_reutiliza_el_historial():
    historial_inicial = obtener_historial("sesion_a")
    historial_inicial.add_user_message("Practico a 60 BPM.")

    historial_recuperado = obtener_historial("sesion_a")

    assert historial_recuperado is historial_inicial
    assert historial_recuperado.messages[0].content == "Practico a 60 BPM."


def test_distintos_session_id_no_comparten_el_historial():
    historial_a = obtener_historial("sesion_a")
    historial_a.add_user_message("Practico a 60 BPM.")

    historial_b = obtener_historial("sesion_b")

    assert historial_b is not historial_a
    assert historial_b.messages == []
