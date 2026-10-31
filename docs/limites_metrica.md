# Límites de la métrica de evaluación

## Qué mide

La métrica normaliza y tokeniza la respuesta y la referencia, cuenta las palabras coincidentes —incluidas sus repeticiones— y calcula precisión, cobertura y F1. Mide coincidencia textual; no determina por sí sola si una respuesta es correcta o adecuada para la práctica musical.

## Modos de falla conocidos

- Una respuesta puede expresar correctamente la idea con otras palabras y obtener un F1 bajo. En el caso `rhythmmentor_18_molestia_explicita`, la respuesta indicó que se debía registrar el dolor en la muñeca; se calificó como factual y completa, pero su F1 fue 0.143.

- Las respuestas largas pueden obtener F1 bajo aunque incluyan el contenido requerido. En `rhythmmentor_10_suma_ejercicios`, la respuesta indicó tres ejercicios de cuatro minutos, que sumaban los 12 minutos solicitados. También asumió un tempo de 60 BPM que no se había indicado; se calificó como parcialmente correcta y obtuvo F1 0.202.

- La métrica no distingue por sí sola entre una recomendación adicional correcta y una que no está respaldada por la consulta o la referencia. Por ejemplo, `rhythmmentor_12_progresion_gradual` incluyó la sugerencia de aumentar entre 5 y 10 BPM. La idea de progresar gradualmente coincide con la referencia, pero ese rango adicional no se pudo validar con ella; el caso obtuvo F1 0.149.

- Un F1 alto tampoco demuestra por sí solo que una respuesta sea correcta. En esta muestra, los cinco casos con mayor F1 sí fueron calificados como correctos y completos, pero una muestra de diez casos no permite concluir que siempre ocurra así.

No se observaron contradicciones ni datos numéricos incorrectos en los diez casos revisados. Por eso, esta revisión no permite afirmar cómo puntuará la métrica esos tipos de error.

## Muestra revisada

Se revisaron 10 de las 20 respuestas generadas el 30/10/2026: los cinco casos con menor F1 (`rhythmmentor_18_molestia_explicita`, `rhythmmentor_12_progresion_gradual`, `rhythmmentor_19_no_aumento_bruso`, `rhythmmentor_16_registro_tempo_y_nivel` y `rhythmmentor_10_suma_ejercicios`) y los cinco con mayor F1 (`rhythmmentor_04_tempo`, `rhythmmentor_09_duracion_sesion`, `rhythmmentor_11_tempo_inicial`, `rhythmmentor_13_historial_hi_hat` y `rhythmmentor_03_duracion_real`).

La revisión manual está registrada en `docs/revision_manual.json`. Se aplicó la rúbrica de corrección factual, completitud y contradicción, con una nota por caso.

## Recomendación de uso

Usar precisión, cobertura y F1 como indicadores de coincidencia textual al comparar respuestas para las mismas consultas y referencias. No usarlos como única medida de calidad. Revisar manualmente las respuestas con BPM, duraciones, afirmaciones sobre molestias o recomendaciones adicionales, y también los resultados con puntajes inesperadamente altos o bajos.