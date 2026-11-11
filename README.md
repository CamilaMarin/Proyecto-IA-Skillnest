# RhythmMentor

**Proyecto en desarrollo como parte de la Especialización en Desarrollo con IA Generativa (Accenture).**

RhythmMentor busca ayudar a personas que practican música de forma autodidacta a organizar sus sesiones y avanzar progresivamente. En esta etapa inicial, el proyecto se enfoca en personas principiantes que practican batería electrónica. Su alcance y funcionalidades se ampliarán durante el curso.

La arquitectura puede adaptarse para consumir APIs de distintos proveedores de modelos de IA. La integración implementada actualmente utiliza Google Gemini. Para cambiar de proveedor, hay que adaptar la URL, la autenticación, el formato de la solicitud y el procesamiento de la respuesta; cambiar solamente la API key no es suficiente.

## Requisitos

- Python **3.12 o superior**.
- Git.
- Una API key válida de Google Gemini para ejecutar la integración actual.
- Conexión a internet para instalar dependencias y enviar solicitudes al proveedor.
- Terminal en macOS/Linux o PowerShell en Windows.

Las solicitudes a la API pueden estar sujetas a límites o costos según la cuenta y las condiciones del proveedor.

## Cómo empezar

Ejecuta los comandos desde la raíz del repositorio.

### 1. Clona el repositorio

```bash
git clone https://github.com/CamilaMarin/Proyecto-IA-Skillnest.git
cd Proyecto-IA-Skillnest
```

### 2. Crea un entorno virtual

**macOS/Linux**

```bash
python3 -m venv venv
```

**Windows (PowerShell)**

```powershell
py -m venv venv
```

### 3. Activa el entorno virtual

**macOS/Linux**

```bash
source venv/bin/activate
```

**Windows (PowerShell)**

```powershell
.\venv\Scripts\Activate
```

### 4. Instala las dependencias

Con el entorno virtual activado:

```bash
python -m pip install -r requirements.txt
```

En macOS/Linux, si el comando `python` no está disponible, usa `python3`:

```bash
python3 -m pip install -r requirements.txt
```

Usa también `python3` en lugar de `python` en los comandos de ejecución de este README si lo necesitas en macOS/Linux.

### 5. Configura la API key

Crea `.env` copiando `.env.example`.

**macOS/Linux**

```bash
cp .env.example .env
```

**Windows (PowerShell)**

```powershell
Copy-Item .env.example .env
```

Abre `.env` y reemplaza el valor de ejemplo por una API key válida de Google Gemini:

```dotenv
GEMINI_API_KEY=tu_api_key_de_gemini_aqui
```

La integración actual busca la variable `GEMINI_API_KEY`. El archivo `.env` contiene credenciales, está excluido por `.gitignore` y no debe subirse ni compartirse. `.env.example` solo debe contener nombres de variables y valores ficticios, nunca una llave real.

## Ejecutar los programas

Ejecuta los comandos desde la raíz del repositorio. Los programas que consultan Gemini necesitan una API key válida y pueden generar costos.

### Enviar una solicitud a Gemini

```bash
python src/consumir_gemini.py
```

El programa envía una solicitud de prueba a Gemini, mide la latencia, estima el costo con las tarifas configuradas en el código y valida que la respuesta sea JSON.

### Validar el banco de prompts

```bash
python src/consistencia.py
```

El programa recorre los prompts de src/prompts/banco.py y registra cuántas respuestas incluyen las claves esperadas. Los resultados se guardan en src/prompts/registro_resultados.json; cada ejecución sobrescribe ese archivo. La validación comprueba el formato JSON y las claves, no la calidad semántica de la respuesta.

### Comparar modelos

```bash
python src/comparar_modelos.py
```

src/comparar_modelos.py compara latencia, costo estimado y respuestas de los modelos de la constante MODELOS, utilizando las preguntas de PROMPTS. La solicitud incluye una instrucción de sistema de RhythmMentor y usa response_schema=None, así que no fuerza una respuesta JSON estructurada.

Con la configuración actual —dos preguntas, cuatro modelos y cuatro repeticiones— puede enviar hasta 32 solicitudes. La cantidad cambia al modificar esos valores. El informe Markdown, que incluye las respuestas, se guarda en docs/.

Antes de interpretar los resultados:

- Verifica que los nombres de los modelos en `MODELOS` estén disponibles para tu cuenta.
- Mantén actualizadas las tarifas de entrada y salida. El cálculo usa valores en USD por token; para convertir precios publicados por millón de tokens, divide cada precio por un millón.
- Ten presente que el programa registra las respuestas, la latencia y el costo; no evalúa automáticamente la calidad musical de las respuestas.
- La ejecución puede estar sujeta a límites o costos de tu cuenta.
- Los resultados obtenidos con distintas instrucciones de sistema o esquemas de respuesta pueden no ser directamente comparables.

### Probar el pipeline de texto

```bash
python -m src.pipeline_texto
```

El programa envía una pregunta de ejemplo al modelo y compara sus tokens con un texto de referencia, antes y después de normalizar el texto. Actualmente usa un ejemplo sobre Python; no es una evaluación específica de las respuestas de RhythmMentor.

### Calcular métricas de precisión, cobertura y F1

```bash
python -m src.precision
```

El programa evalúa 20 casos relacionados con RhythmMentor. Para cada consulta, guarda la referencia, la respuesta generada y sus métricas de precisión, cobertura y F1 en docs/resultados_metricas.json.

Los resultados se guardan después de cada respuesta. Si la ejecución se interrumpe, al volver a ejecutar el comando se omiten los casos que ya tienen resultado y se continúa con los pendientes. Las solicitudes a Gemini pueden generar costos.

Estas métricas comparan palabras y sus frecuencias. No determinan por sí solas si una respuesta es semánticamente correcta ni si una recomendación musical es adecuada.

### Revisar resultados manualmente

```bash
python -m src.revision_manual
```
El programa selecciona los cinco casos con menor F1 y los cinco con mayor F1. Para cada uno solicita una valoración de corrección factual, completitud y contradicción, además de una nota justificativa.

La revisión se guarda en docs/revision_manual.json. Deben existir al menos 20 resultados en docs/resultados_metricas.json antes de iniciar la revisión.

### Diseñar una sesión de práctica con LangChain

```bash
python -m src.cadena_tres_pasos
```
La cadena procesa una solicitud de RhythmMentor en tres pasos: extrae el nivel, el objetivo, la duración y el BPM; diseña una sesión; y revisa el plan frente a los requisitos originales. La respuesta se muestra en la consola.

Cada ejecución realiza tres llamadas a Gemini y puede estar sujeta a límites o costos de la cuenta. La prueba automatizada usa un modelo simulado y no consume llamadas a la API.

### Enrutar solicitudes de RhythmMentor

```bash
python -m src.enrutamiento
```
El programa clasifica la solicitud y la dirige a una ruta: crear una sesión, proponer un ejercicio, ajustar la dificultad o responder una consulta general. La ruta para crear una sesión reutiliza la cadena LangChain de tres pasos.

Cada ejecución realiza una llamada al modelo para clasificar la solicitud y otra para generar la respuesta. La ruta de creación de sesión realiza tres llamadas adicionales. Por ello, una ejecución puede realizar entre dos y cuatro llamadas a Gemini y estar sujeta a límites o costos de la cuenta.

Si falla la creación de una sesión, el programa registra el nivel, el tipo y el mensaje del error en `error.log`, y entrega una respuesta de respaldo. Si falla otra parte del flujo, `procesar_mensaje_seguro` registra el error y devuelve una respuesta segura. El archivo de log está excluido del repositorio mediante `.gitignore`.

### Agente con herramientas y memoria

El agente sin memoria se puede ejecutar desde la raíz del proyecto:

```bash
python -m src.agente_con_herramientas
```
Usa `distribuir_duracion_sesion` para repartir el tiempo disponible entre ejercicios. Esta herramienta solo calcula; no guarda sesiones.

El agente con memoria y guardado controlado se ejecuta con:

```bash
python -m src.agente_con_memoria
```

La memoria de conversación se mantiene en RAM y se separa por `session_id`. Se pierde al cerrar el proceso y no reemplaza el historial persistente de prácticas.

El agente solo usa `guardar_sesion_practica` si la persona pide guardar una sesión. Antes de escribir en SQLite, muestra los datos y espera aprobación en la terminal. Escribe `s` y presiona Enter antes de que transcurran 15 segundos para aprobar. El rechazo, el timeout o la falta de una terminal interactiva cancelan el guardado. Ejecutar este ejemplo genera solicitudes a Gemini y puede tener costos.

Las sesiones aprobadas se guardan en `data/sesiones.db`. La carpeta `data/` está excluida por `.gitignore`; no subas allí datos personales. El repositorio permite consultar, listar, editar y eliminar sesiones. La eliminación es permanente y todavía no está disponible como herramienta del agente.

## Estructura del proyecto

```text
.
├── data/                         # Base local; excluida de Git
├── docs/
│   ├── comparativas de modelos
│   ├── decisión y diagramas de arquitectura
│   ├── limites_autonomia_agente.md
│   ├── limites_metrica.md
│   ├── registro_rate_limit.md
│   ├── resultados_metricas.json
│   └── revision_manual.json
├── src/
│   ├── agente_con_herramientas.py
│   ├── agente_con_memoria.py
│   ├── cadena.py
│   ├── cadena_tres_pasos.py
│   ├── cliente.py
│   ├── comparar_modelos.py
│   ├── consistencia.py
│   ├── consumir_gemini.py
│   ├── enrutamiento.py
│   ├── herramientas_rhythmmentor.py
│   ├── pipeline_limpieza.py
│   ├── pipeline_texto.py
│   ├── precision.py
│   ├── repositorio_sesiones.py
│   ├── revision_manual.py
│   └── prompts/
│       ├── banco.py
│       └── registro_resultados.json
├── tests/
│   ├── test_agente_con_memoria.py
│   ├── test_cadena_tres_pasos.py
│   ├── test_cliente.py
│   ├── test_guardar_sesion_hitl.py
│   ├── test_orquestacion.py
│   ├── test_pipeline.py
│   ├── test_precision.py
│   └── test_repositorio_sesiones.py
├── .env.example
├── .gitignore
├── pytest.ini
├── README.md
├── requirements.txt
└── trazas_agente.jsonl
```
- `src/agente_con_herramientas.py`: ejecuta el agente sin memoria, que puede repartir el tiempo entre ejercicios.
- `src/agente_con_memoria.py`: ejecuta el agente con historial temporal separado por `session_id` y registro de trazas.
- `src/cadena.py`: contiene una cadena LangChain de ejemplo para explicar un concepto musical.
- `src/cadena_tres_pasos.py`: construye y ejecuta una cadena LangChain que extrae los requisitos de una sesión, diseña el plan y lo revisa frente a la solicitud original.
- `src/consumir_gemini.py`: construye y envía solicitudes a Gemini, extrae respuestas, mide latencia, calcula costos y valida respuestas JSON.
- `src/cliente.py`: ofrece funciones para consultar el modelo, reintentar ante TimeoutError y acumular costo y tokens de la sesión.
- `src/enrutamiento.py`: clasifica las solicitudes de RhythmMentor y las dirige a la ruta correspondiente; maneja fallos con un fallback y una respuesta segura.
- `src/herramientas_rhythmmentor.py`: define la distribución de duración y el guardado con aprobación humana.
- `src/prompts/banco.py`: contiene prompts de RhythmMentor, instrucciones de sistema, ejemplos, claves esperadas y esquemas de respuesta.
- `src/repositorio_sesiones.py`: guarda, consulta, edita y elimina sesiones en SQLite.
- `src/consistencia.py`: ejecuta los prompts del banco y registra cuántas respuestas pasan la validación de formato y claves.
- `src/comparar_modelos.py`: compara respuestas, latencia y costo estimado y guarda un informe con las respuestas en docs/.
- `src/pipeline_limpieza.py`: normaliza texto y lo convierte en tokens.
- `src/pipeline_texto.py`: compara coincidencias de tokens en un ejemplo de texto crudo y procesado.
- `src/precision.py`: calcula precisión, cobertura y F1 sobre tokens, ejecuta casos y guarda los resultados en `docs/resultados_metricas.json`.
- `src/revision_manual.py`: permite revisar los diez resultados seleccionados con la rúbrica cualitativa.
- `docs/revision_manual.json`: conserva las valoraciones y notas de la revisión manual.
- `docs/limites_autonomia_agente.md`: documenta riesgos, aprobación humana y revisión de trazas.
- `docs/limites_metrica.md`: describe qué mide F1, los límites observados en la muestra y cómo usar la métrica.
- `docs/resultados_metricas.json`: conserva las 20 consultas, referencias, respuestas y métricas de la evaluación.
- `tests/`: contiene pruebas automatizadas del cliente, los pipelines de texto y métricas, las cadenas LangChain y el enrutamiento.
- `tests/test_agente_con_memoria.py`: verifica que se reutilice el historial de una misma sesión y que distintos `session_id` no compartan mensajes.
- `tests/test_repositorio_sesiones.py`: verifica guardado, lectura, edición, borrado y validación usando una base SQLite temporal.
- `tests/test_guardar_sesion_hitl.py`: simula aprobación, rechazo y timeout; verifica que los datos inválidos o no aprobados no se guarden.
- `tests/test_cadena_tres_pasos.py`: prueba con un modelo simulado que los tres pasos se conectan y que la revisión recibe los requisitos y el plan, sin llamar a Gemini.
- `tests/test_orquestacion.py`: prueba la normalización de las intenciones, las rutas disponibles y el manejo de fallos con modelos simulados.
- `pytest.ini`: indica dónde buscar las pruebas al ejecutar pytest.
- `requirements.txt`: contiene las dependencias necesarias para instalar el proyecto.
- `trazas_agente.jsonl`: registra entradas, llamadas a herramientas, observaciones y respuestas; usa datos de prueba sin información sensible.
- `.env.example`: plantilla de variables de entorno sin credenciales reales.
- `.gitignore`: indica a Git qué archivos debe ignorar, incluidos .env y el entorno virtual.

## Seguridad y credenciales

- No escribas API keys, contraseñas ni tokens directamente en el código.
- No subas .env al repositorio.
- Usa valores ficticios en .env.example; nunca pongas allí credenciales reales.
- El nombre de la variable configurada debe coincidir con el que lee el código. Actualmente es GEMINI_API_KEY.
- Para utilizar otro proveedor, adapta y prueba la integración, incluida la autenticación y el formato de sus solicitudes y respuestas.

## Pruebas

Desde la raíz del repositorio, ejecuta:

```bash
python -m pytest tests -v
```

En macOS/Linux, si python no está disponible:

```bash
python3 -m pytest tests -v
```

Las pruebas usan pytest, unittest.mock y RunnableLambda para simular respuestas y fallos. No envían solicitudes reales a Gemini ni necesitan una API key.

La suite cubre:

- enviar_peticion: respuestas exitosas, credenciales inválidas (401 y 403), límite de uso (429), errores del servidor, errores de conexión y otros errores HTTP.
- con_reintento: agotamiento de intentos, propagación de excepciones que no deben reintentarse y recuperación tras fallos temporales de tipo TimeoutError.
- registrar_costo: cálculo y acumulación del costo y los tokens de varias operaciones.
- consultar_modelo: conversión de un timeout agotado, propagación de ValueError y flujo exitoso.
- calcular_costos y parsear_respuesta_json: validación de los metadatos de tokens y rechazo de JSON que no sea un objeto.
- Procesamiento y métricas de texto: normalización, casos con referencia vacía, cálculo de métricas y resumen vacío.
- Cadena LangChain: verifica que se ejecuten los tres pasos y que la revisión reciba los requisitos y el plan, usando un modelo simulado.
- Enrutamiento: normalización de intenciones, rutas de RhythmMentor, fallback de creación de sesión y registro del error original.
- Memoria del agente: reutilización del historial con el mismo `session_id` y aislamiento entre IDs distintos.
- Repositorio SQLite: persistencia, lectura, edición, eliminación y validación con una base temporal.
- Guardado HITL: aprobación, rechazo, timeout y rechazo de planes con duraciones inconsistentes, usando mocks y sin llamar a Gemini.


## Registro del ensayo de instalación limpia

### Ensayo del 23/10/2026

- **Encontrado:** El README no incluía una alternativa con python3 para macOS/Linux ni explicaba la configuración de la comparativa de modelos.
- **Corregido:** Se documentaron los comandos multiplataforma, la instrucción de sistema, response_schema=None y el paso del modelo desde MODELOS. En consumir_gemini.py se configuró gemini-3.5-flash-lite con las tarifas registradas en ese momento.
- **Resultado:** La instalación y ejecución completas en un entorno limpio quedaron pendientes de validar tras esos cambios. La disponibilidad de modelos y las tarifas deben verificarse con el proveedor antes de cada comparativa.

### Ensayo del 24/10/2026

- **Encontrado:** No se encontraron problemas durante la instalación limpia.
- **Corregido:** No fue necesario realizar correcciones adicionales.
- **Resultado:** La instalación y ejecución del proyecto se completaron satisfactoriamente en un entorno limpio.
