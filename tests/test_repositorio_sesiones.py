import pytest

from src.repositorio_sesiones import RepositorioSesiones


@pytest.fixture
def repositorio(tmp_path):
    return RepositorioSesiones(tmp_path / "sesiones_test.db")


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


def test_guarda_y_recupera_una_sesion(repositorio, tmp_path):
    guardada = repositorio.guardar_sesion(**datos_sesion())

    # Una nueva instancia confirma que los datos quedaron en SQLite.
    otro_repositorio = RepositorioSesiones(
        tmp_path / "sesiones_test.db"
    )
    recuperada = otro_repositorio.obtener_sesion(guardada["id"])

    assert recuperada["nivel"] == "principiante"
    assert recuperada["duracion_total_minutos"] == 10
    assert recuperada["ejercicios"] == datos_sesion()["ejercicios"]


def test_edita_una_sesion(repositorio):
    guardada = repositorio.guardar_sesion(**datos_sesion())

    actualizada = repositorio.actualizar_sesion(
        guardada["id"],
        objetivo="Practicar independencia de manos",
    )

    assert actualizada["objetivo"] == "Practicar independencia de manos"


def test_elimina_una_sesion(repositorio):
    guardada = repositorio.guardar_sesion(**datos_sesion())

    assert repositorio.eliminar_sesion(guardada["id"]) is True
    assert repositorio.obtener_sesion(guardada["id"]) is None
    assert repositorio.eliminar_sesion(guardada["id"]) is False


def test_rechaza_duraciones_que_no_suman_el_total(repositorio):
    datos = datos_sesion()
    datos["ejercicios"][0]["duracion_minutos"] = 4

    with pytest.raises(ValueError, match="debe coincidir"):
        repositorio.guardar_sesion(**datos)