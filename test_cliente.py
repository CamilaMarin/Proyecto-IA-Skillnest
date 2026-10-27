from unittest.mock import patch, Mock, call

import pytest
import requests

import cliente
from cliente import con_reintento, consultar_modelo, registrar_costo
from src.consumir_gemini import enviar_peticion



@pytest.fixture(autouse=True)
def reiniciar_costo_total():
    cliente.costo_total_sesion = 0.0
    cliente.total_tokens_sesion = 0
    yield

@pytest.mark.parametrize("status_code", [401, 403])
def test_enviar_peticion_credencial_invalida(status_code):
    respuesta_falsa = Mock(status_code=status_code)

    with patch("src.consumir_gemini.requests.post", return_value=respuesta_falsa):
        with pytest.raises(ValueError):
            enviar_peticion("https://ejemplo.invalid",{"pregunta":"test"})

def test_enviar_peticion_limite_de_uso():
    respuesta_falsa = Mock(status_code=429)

    with patch("src.consumir_gemini.requests.post", return_value=respuesta_falsa):
        with pytest.raises(TimeoutError):
            enviar_peticion("https://ejemplo.invalid",{"pregunta":"test"})


@pytest.mark.parametrize("status_code", [500, 503])
def test_enviar_peticion_error_servidor(status_code):
    respuesta_falsa = Mock(status_code=status_code)

    with patch(
        "src.consumir_gemini.requests.post",
        return_value=respuesta_falsa,
    ):
        with pytest.raises(TimeoutError):
            enviar_peticion(
                "https://ejemplo.invalid",
                {"pregunta": "test"},
            )

@pytest.mark.parametrize(
    "error",
    [
        requests.exceptions.ConnectionError("sin conexión"),
        requests.exceptions.Timeout("tiempo agotado"),
    ],
)
def test_enviar_peticion_error_de_conexion(error):
    with patch(
        "src.consumir_gemini.requests.post",
        side_effect=error,
    ):
        with pytest.raises(RuntimeError):
            enviar_peticion(
                "https://ejemplo.invalid",
                {"pregunta": "test"},
            )


def test_enviar_peticion_error_http_generico():
    respuesta_falsa = Mock(status_code=400)

    with patch(
        "src.consumir_gemini.requests.post",
        return_value=respuesta_falsa,
    ):
        with pytest.raises(RuntimeError):
            enviar_peticion(
                "https://ejemplo.invalid",
                {"pregunta": "test"},
            )

def test_enviar_peticion_exito():
    respuesta_falsa = Mock(status_code=200)
    respuesta_falsa.json.return_value = {"texto": "respuesta simulada"}

    with patch("src.consumir_gemini.requests.post", return_value=respuesta_falsa):
        resultado = enviar_peticion("https://ejemplo.invalid",{"pregunta": "test"})

    assert resultado == {"texto": "respuesta simulada"}

def test_con_reintento_agota_intentos():
    funcion = Mock(side_effect=TimeoutError("simulado"))

    with patch("cliente.time.sleep"):
        with pytest.raises(TimeoutError, match="simulado"):
            con_reintento(funcion, intentos=3)

    assert funcion.call_count == 3

def test_con_reintento_no_reintenta_value_error():
    funcion = Mock(side_effect=ValueError("dato inválido"))

    with pytest.raises(ValueError, match="dato inválido"):
        cliente.con_reintento(funcion, intentos=3)

    assert funcion.call_count == 1

def test_con_reintento_reintenta_y_luego_tiene_exito():
    funcion = Mock(
        side_effect=[
            TimeoutError("primer fallo"),
            TimeoutError("segundo fallo"),
            "respuesta correcta",
        ]
    )

    with (
        patch("cliente.random.uniform", return_value=0),
        patch("cliente.time.sleep") as dormir,
    ):
        resultado = cliente.con_reintento(funcion, intentos=3)

    assert resultado == "respuesta correcta"
    assert funcion.call_count == 3
    assert dormir.call_args_list == [call(2), call(4)]

def test_registrar_costo_acumula_costo_y_tokens():
    respuesta = {
        "usageMetadata": {
            "promptTokenCount": 100,
            "candidatesTokenCount": 20,
            "thoughtsTokenCount": 5,
            "totalTokenCount": 125,
        }
    }

    costo = cliente.registrar_costo(respuesta)

    assert costo == pytest.approx(0.0000925)
    assert cliente.costo_total_sesion == pytest.approx(0.0000925)
    assert cliente.total_tokens_sesion == 125

def test_registrar_costo_acumula_varias_operaciones():
    respuesta = {
        "usageMetadata": {
            "promptTokenCount": 100,
            "candidatesTokenCount": 20,
            "thoughtsTokenCount": 5,
            "totalTokenCount": 125,
        }
    }

    cliente.registrar_costo(respuesta)
    cliente.registrar_costo(respuesta)

    assert cliente.costo_total_sesion == pytest.approx(0.000185)
    assert cliente.total_tokens_sesion == 250

def test_consultar_modelo_convierte_error():
    error_simulado = TimeoutError("simulado")

    with patch("cliente.con_reintento", side_effect=error_simulado):
        with pytest.raises(RuntimeError):
            consultar_modelo("pregunta de prueba")

def test_consultar_modelo_propaga_value_error():
    error_original = ValueError("credencial inválida")

    with patch("cliente.con_reintento", side_effect=error_original):
        with pytest.raises(ValueError, match="credencial inválida") as error_recibido:
            consultar_modelo("pregunta de prueba")

    assert error_recibido.value is error_original

def test_consultar_modelo_devuelve_texto_y_registra_costo():
    respuesta = {"respuesta_simulada": True}

    with (
        patch("cliente.armar_peticion", return_value=("url", {"body": "test"})),
        patch("cliente.con_reintento", return_value=respuesta) as reintentar,
        patch("cliente.registrar_costo") as registrar,
        patch("cliente.extraer_texto", return_value="texto generado") as extraer,
    ):
        resultado = cliente.consultar_modelo("pregunta de prueba")

    assert resultado == "texto generado"
    reintentar.assert_called_once()
    registrar.assert_called_once_with(respuesta)
    extraer.assert_called_once_with(respuesta)