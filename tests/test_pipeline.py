from src.pipeline_limpieza import procesar_texto
from src.pipeline_texto import calcular_coincidencia

def test_calcular_coincidencia_con_referencia_vacia_devuelve_cero():
    assert calcular_coincidencia([], ["bateria"]) == 0.0
    
def test_procesar_texto_normaliza_mayusculas_y_puntuacion():
    resultado = procesar_texto("El Cielo, es AZUL!")
    assert resultado == ["el", "cielo", "es", "azul"]

def test_procesar_texto_solo_puntuacion_devuelve_lista_vacia(): 
    resultado = procesar_texto("¡¡¡...!!!")  
    assert resultado == [] 

