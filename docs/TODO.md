# Pruebas pendientes

Lista de pruebas unitarias que conviene agregar en futuras iteraciones de RhythmMentor. Las pruebas deben usar mocks o datos temporales para evitar llamadas reales a Gemini y escrituras sobre los resultados del proyecto.

## Cliente y respuestas del proveedor

- [ ] `armar_peticion`: rechazar preguntas vacías y comprobar que incluye `system_instruction`, `response_schema` y el modelo indicado.
- [ ] `enviar_peticion`: convertir una respuesta HTTP 200 con JSON inválido en `RuntimeError`.
- [ ] `extraer_texto`: extraer texto de una respuesta válida y manejar respuestas malformadas o sin candidatos/texto.
- [ ] `calcular_costos`: cubrir ausencia de `usageMetadata`, falta de campos obligatorios y valores inválidos en los tokens de entrada, salida y razonamiento.
- [ ] `parsear_respuesta_json`: probar JSON malformado, JSON válido, bloques Markdown con JSON y ausencia de claves esperadas.
- [ ] `con_reintento`: decidir y probar el comportamiento para `intentos` igual a cero o negativo. Actualmente el ciclo no ejecuta la función y devuelve `None`.
- [ ] `con_reintento`: definir y probar si debe respetar el encabezado `Retry-After` cuando el proveedor responde HTTP 429; actualmente usa su espera exponencial.

## Métricas y guardado incremental

- [ ] `calcular_coincidencia`: probar coincidencia exacta, parcial y nula, además de aclarar el comportamiento esperado ante tokens repetidos.
- [ ] `calcular_precision_cobertura_f1` y `resumir_metricas`: probar coincidencia completa, tokens repetidos y promedio con varios resultados.
- [ ] `guardar_resultados`: verificar la escritura JSON y que reemplaza el archivo temporal por el archivo final.
- [ ] `cargar_resultados`: probar archivo inexistente, migración de resultados antiguos, duplicados, resultados incompatibles y JSON inválido.
- [ ] `ejecutar_evaluacion`: simular respuestas del cliente para verificar que omite casos ya guardados, guarda después de cada éxito y conserva el avance cuando una llamada falla.

## Procesamiento manual y scripts de evaluación

- [ ] `revision_manual.py`: probar la validación de entradas, la selección de casos y el rechazo cuando ya existe el archivo de revisión, usando archivos temporales y entradas simuladas.
- [ ] `comparar_modelos.py`: probar el cálculo del resumen y la escritura Markdown con respuestas simuladas, sin contactar al proveedor.
- [ ] `consistencia.py`: separar la lógica ejecutable de la importación del módulo y probar validación y registro con respuestas simuladas, sin llamadas reales.
- [ ] `enrutamiento.py`: probar que el fallback registra el tipo y mensaje del error en un archivo de log temporal, sin incluir un traceback.

## Documentación técnica de funciones y pruebas

- [ ] Añadir docstrings a las funciones públicas de `src/`, explicando propósito, parámetros, retorno y excepciones relevantes.
- [ ] Crear `docs/pruebas.md` con el comando para ejecutar pytest y un resumen de qué cubre cada archivo de pruebas.
- [ ] Evaluar MkDocs con mkdocstrings para generar una referencia navegable desde Markdown y los docstrings; incorporarlo solo si el proyecto necesita un sitio de documentación.
- [ ] Cuando RhythmMentor tenga endpoints FastAPI, aprovechar su documentación OpenAPI interactiva para las rutas HTTP y mantener aparte la referencia de funciones internas y pruebas.

## Integración futura con la batería Alesis Nitro Mesh

- [ ] Confirmar que el módulo Nitro Mesh aparece como dispositivo USB-MIDI en el Mac.
- [ ] Comprobar qué eventos MIDI envía cada pad y documentar la correspondencia entre notas MIDI y componentes de la batería.
- [ ] Probar la recepción de golpes MIDI y distinguir los datos disponibles —como nota y velocidad— de métricas que RhythmMentor tendría que calcular.
- [ ] Definir qué datos de una sesión guardar, por ejemplo fecha, duración, ejercicio y resumen de eventos o métricas.
- [ ] Probar el guardado y la lectura de sesiones capturadas desde el instrumento.
- [ ] Manejar y probar desconexiones, ausencia de eventos y cierre de la sesión.
- [ ] Mantener pruebas automatizadas con eventos MIDI simulados; documentar por separado las comprobaciones manuales que requieren conectar la batería.

