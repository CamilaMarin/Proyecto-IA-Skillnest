import pytest

from src.precision import (
    calcular_precision_cobertura_f1,
    resumir_metricas,
)


def test_metricas_coincidencia_parcial():
    resultado = calcular_precision_cobertura_f1(
        ["bateria", "ritmo"],
        ["bateria", "tempo"],
    )

    assert resultado["precision"] == pytest.approx(0.5)
    assert resultado["cobertura"] == pytest.approx(0.5)
    assert resultado["f1"] == pytest.approx(0.5)


@pytest.mark.parametrize(
    "referencia,respuesta",
    [
        ([], []),
        (["bateria"], []),
        ([], ["bateria"]),
    ],
)
def test_metricas_con_lista_vacia_devuelven_ceros(referencia, respuesta):
    resultado = calcular_precision_cobertura_f1(referencia, respuesta)

    assert resultado == {
        "precision": 0.0,
        "cobertura": 0.0,
        "f1": 0.0,
    }


def test_resumir_metricas_sin_resultados_devuelve_ceros():
    assert resumir_metricas([]) == {
        "precision_promedio": 0.0,
        "cobertura_promedio": 0.0,
        "f1_promedio": 0.0,
    }