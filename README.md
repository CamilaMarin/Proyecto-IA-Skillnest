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

El programa consulta al modelo con tres casos de ejemplo, calcula métricas de coincidencia entre los tokens de cada respuesta y su referencia y guarda las respuestas y métricas en docs/resultados_metricas.json. Cada ejecución sobrescribe ese archivo.

Estas métricas comparan palabras y sus frecuencias. No miden por sí solas si una respuesta es semánticamente correcta ni si un ejercicio musical es adecuado.

## Estructura del proyecto

```text
.
├── docs/
│   ├── comparativas de modelos
│   ├── decisión y diagramas de arquitectura
│   ├── resultados_metricas.json
│   └── registro_rate_limit.md
├── src/
│   ├── cliente.py
│   ├── comparar_modelos.py
│   ├── consistencia.py
│   ├── consumir_gemini.py
│   ├── pipeline_limpieza.py
│   ├── pipeline_texto.py
│   ├── precision.py
│   └── prompts/
│       ├── banco.py
│       └── registro_resultados.json
├── tests/
│   ├── test_cliente.py
│   ├── test_pipeline.py
│   └── test_precision.py
├── .env.example
├── .gitignore
├── pytest.ini
├── README.md
└── requirements.txt
```

- src/consumir_gemini.py: construye y envía solicitudes a Gemini, extrae respuestas, mide latencia, calcula costos y valida respuestas JSON.
- src/cliente.py: ofrece funciones para consultar el modelo, reintentar ante TimeoutError y acumular costo y tokens de la sesión.
- src/prompts/banco.py: contiene prompts de RhythmMentor, instrucciones de sistema, ejemplos, claves esperadas y esquemas de respuesta.
- src/consistencia.py: ejecuta los prompts del banco y registra cuántas respuestas pasan la validación de formato y claves.
- src/comparar_modelos.py: compara respuestas, latencia y costo estimado y guarda un informe con las respuestas en docs/.
- src/pipeline_limpieza.py: normaliza texto y lo convierte en tokens.
- src/pipeline_texto.py: compara coincidencias de tokens en un ejemplo de texto crudo y procesado.
- src/precision.py: calcula precisión, cobertura y F1 sobre tokens, ejecuta casos de ejemplo y guarda los resultados en docs/resultados_metricas.json.
- tests/: contiene pruebas automatizadas del cliente, del procesamiento de texto y de las métricas.
- pytest.ini: indica dónde buscar las pruebas al ejecutar pytest.
- requirements.txt: contiene las dependencias necesarias para instalar el proyecto.
- .env.example: plantilla de variables de entorno sin credenciales reales.
- .gitignore: indica a Git qué archivos debe ignorar, incluidos .env y el entorno virtual.

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

Las pruebas usan pytest y unittest.mock para simular respuestas HTTP y errores. No envían solicitudes reales a Gemini ni necesitan una API key.

La suite cubre:

- enviar_peticion: respuestas exitosas, credenciales inválidas (401 y 403), límite de uso (429), errores del servidor, errores de conexión y otros errores HTTP.
- con_reintento: agotamiento de intentos, propagación de excepciones que no deben reintentarse y recuperación tras fallos temporales de tipo TimeoutError.
- registrar_costo: cálculo y acumulación del costo y los tokens de varias operaciones.
- consultar_modelo: conversión de un timeout agotado, propagación de ValueError y flujo exitoso.
- calcular_costos y parsear_respuesta_json: validación de los metadatos de tokens y rechazo de JSON que no sea un objeto.
- Procesamiento y métricas de texto: normalización, casos con referencia vacía, cálculo de métricas y resumen vacío.

## Registro del ensayo de instalación limpia

### Ensayo del 23/10/2026

- **Encontrado:** El README no incluía una alternativa con python3 para macOS/Linux ni explicaba la configuración de la comparativa de modelos.
- **Corregido:** Se documentaron los comandos multiplataforma, la instrucción de sistema, response_schema=None y el paso del modelo desde MODELOS. En consumir_gemini.py se configuró gemini-3.5-flash-lite con las tarifas registradas en ese momento.
- **Resultado:** La instalación y ejecución completas en un entorno limpio quedaron pendientes de validar tras esos cambios. La disponibilidad de modelos y las tarifas deben verificarse con el proveedor antes de cada comparativa.

### Ensayo del 24/10/2026

- **Encontrado:** No se encontraron problemas durante la instalación limpia.
- **Corregido:** No fue necesario realizar correcciones adicionales.
- **Resultado:** La instalación y ejecución del proyecto se completaron satisfactoriamente en un entorno limpio.
