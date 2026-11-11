# Límites de autonomía: agente con memoria de RhythmMentor

## Herramientas y nivel de riesgo

- `distribuir_duracion_sesion`: bajo; es una herramienta de solo lectura.
  Calcula cómo repartir los minutos entre ejercicios. No escribe datos ni
  modifica sesiones.

- `guardar_sesion_practica`: medio; realiza una escritura local reversible
  en `data/sesiones.db`. Guarda datos de una sesión de práctica. Antes de
  escribir, muestra el contenido y espera aprobación humana.

La memoria de conversación no es una herramienta. Se guarda temporalmente
en `HISTORIALES`, separada por `session_id`, y se pierde al cerrar el proceso.
No es el almacenamiento permanente de sesiones.

## Herramientas que requieren aprobación humana

- `guardar_sesion_practica`: requiere que la persona confirme el resumen antes de escribirlo en SQLite. Solo `s` seguido de Enter aprueba el guardado.
Un rechazo, EOF, una interrupción, la ausencia de terminal interactiva o el vencimiento del timeout de 15 segundos cancela la escritura.

- `eliminar_sesion` existe en el repositorio, pero todavía no está expuesta como herramienta del agente. Elimina permanentemente; si se expone en el futuro, debe tener una aprobación humana antes de ejecutarse.

- `distribuir_duracion_sesion` no requiere aprobación porque solo calcula duraciones y no produce cambios persistentes.

## Revisión de trazas

- Archivo: `trazas_agente.jsonl`, en la raíz del repositorio.
- Frecuencia: revisar cada ejecución durante la validación y después de cada cambio en prompts, herramientas o persistencia. Si el agente se usa de manera regular, revisar las trazas al menos semanalmente.
- Revisar que el guardado ocurra únicamente después de una aprobación, que los datos de la sesión coincidan con la solicitud y que las duraciones sumen el total indicado.
- Comprobar que un rechazo o timeout no cree una sesión. La salida actual no distingue entre ambas causas; ambas se registran como una operación no aprobada o vencida.
- Las trazas conservan la entrada de la persona, los argumentos y las observaciones de las herramientas, y la respuesta final. Usar datos de prueba sin información sensible.
- La función de registro se ejecuta después de una invocación exitosa; las excepciones que interrumpen la invocación no quedan registradas por ella.
- El archivo contiene una traza histórica de logística. No usarla como evidencia de RhythmMentor.

## Qué hacer ante un comportamiento inesperado

1. Suspender el agente o retirar temporalmente `guardar_sesion_practica` de `HERRAMIENTAS`.
2. Revisar la traza correspondiente y el registro guardado en SQLite.
3. Si se guardó una sesión incorrecta, corregirla o eliminarla mediante el repositorio; el borrado permanente requiere autorización humana.
4. Revisar el prompt, el esquema de argumentos y las validaciones del repositorio.
5. Volver a probar el guardado aprobado, el rechazo y el timeout. Confirmar que solo la aprobación crea un registro y revisar las trazas antes de reactivar la herramienta.

## Evidencia revisada

En las trazas actuales hay llamadas reales a las herramientas de distribución y guardado de sesiones. Se observa un guardado aprobado y tres operaciones que no guardaron por rechazo o timeout. Las pruebas automatizadas también simulan aprobación, rechazo, timeout y datos inválidos; no llaman a Gemini.