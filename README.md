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

## Ejecutar la aplicación

### Generar una respuesta con Gemini

```bash
python src/consumir_gemini.py
```

El programa envía una solicitud a Gemini, mide la latencia, estima el costo con las tarifas configuradas en el código e intenta procesar la respuesta como JSON.

### Validar el banco de prompts

```bash
python src/consistencia.py
```

El programa recorre los prompts de `src/prompts/banco.py` y registra cuántas respuestas pasan la validación de claves esperadas. Los resultados se guardan en `src/prompts/registro_resultados.json`; cada ejecución sobrescribe ese archivo.

### Comparar modelos

`src/comparar_modelos.py` compara las respuestas, la latencia y el costo estimado de los modelos definidos en la constante `MODELOS`, usando las preguntas de la constante `PROMPTS`.

La solicitud incluye una instrucción de sistema de RhythmMentor y usa `response_schema=None`; por lo tanto, no fuerza una respuesta JSON estructurada. El nombre del modelo seleccionado se envía mediante el argumento `modelo`. Como esta versión incluye una instrucción de sistema, sus resultados no se deben mezclar directamente con comparativas anteriores realizadas sin ella.

Ejecuta desde la raíz del repositorio:

```bash
python src/comparar_modelos.py
```

En macOS/Linux, si el comando `python` no está disponible:

```bash
python3 src/comparar_modelos.py
```

La comparativa guarda un informe Markdown con los resultados y las respuestas en `docs/`. Con la configuración actual —dos preguntas, cuatro modelos y cuatro repeticiones— puede enviar hasta 32 solicitudes. La cantidad cambiará si modificas esos valores.

Antes de interpretar los resultados:

- Verifica que los nombres de los modelos en `MODELOS` estén disponibles para tu cuenta.
- Mantén actualizadas las tarifas de entrada y salida. El cálculo usa valores en USD por token; para convertir precios publicados por millón de tokens, divide cada precio por un millón.
- Ten presente que el programa registra las respuestas, la latencia y el costo; no evalúa automáticamente la calidad musical de las respuestas.
- La ejecución puede estar sujeta a límites o costos de tu cuenta.

## Estructura del proyecto

```text
.
├── docs/
│   ├── comparativas de modelos
│   ├── decisión de arquitectura
│   └── diagramas de arquitectura
├── src/
│   ├── consumir_gemini.py
│   ├── consistencia.py
│   ├── comparar_modelos.py
│   └── prompts/
│       ├── banco.py
│       └── registro_resultados.json
├── tests/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

- `src/consumir_gemini.py`: construye y envía solicitudes a Gemini, extrae la respuesta, mide latencia, estima el costo y valida respuestas JSON.
- `src/prompts/banco.py`: contiene los prompts de RhythmMentor, sus instrucciones de sistema, ejemplos, claves esperadas y esquemas de respuesta.
- `src/consistencia.py`: ejecuta varias veces los prompts del banco y registra cuántas respuestas pasan la validación de claves.
- `src/prompts/registro_resultados.json`: contiene los resultados de la última ejecución de consistencia.
- `src/comparar_modelos.py`: compara los modelos definidos en el mismo archivo y guarda un informe Markdown en `docs/`.
- `docs/`: contiene documentación técnica, diagramas, la decisión de arquitectura e informes de comparativas.
- `tests/`: directorio reservado para pruebas automatizadas; actualmente no contiene pruebas implementadas.
- `requirements.txt`: dependencias necesarias para instalar el proyecto.
- `.env.example`: plantilla de variables de entorno sin credenciales reales.
- `.gitignore`: indica a Git qué archivos debe ignorar, incluidos `.env` y el entorno virtual.

## Seguridad y uso de credenciales

- No escribas API keys, contraseñas ni tokens directamente en el código.
- No subas `.env` al repositorio.
- Usa valores ficticios en `.env.example`; nunca pongas allí credenciales reales.
- El nombre de la variable configurada debe coincidir con el que lee el código. Actualmente es `GEMINI_API_KEY`.
- Para utilizar otro proveedor, adapta y prueba la integración antes de configurar su API key.

## Pruebas

El directorio `tests/` está reservado para pruebas automatizadas. Actualmente no contiene pruebas implementadas.

## Registro del ensayo de instalación limpia

### Ensayo del 23/10/2026

- **Encontrado:** El README no incluía una alternativa con `python3` para macOS/Linux ni explicaba la configuración actual de la comparativa de modelos.
- **Corregido:** Se documentaron los comandos multiplataforma, la instrucción de sistema, `response_schema=None` y el paso del modelo desde `MODELOS`. En `consumir_gemini.py` se configuró el modelo `gemini-3.5-flash-lite` y sus tarifas: USD 0,30 por millón de tokens de entrada y USD 2,50 por millón de tokens de salida.
- **Resultado:** La configuración del modelo y las tarifas coinciden con la tarifa estándar publicada por Google al 23/10/2026. La instalación y ejecución completas en un entorno limpio quedan pendientes de validar con estos nuevos cambios.

### Ensayo del 24/10/2026

- **Encontrado:** No se encontraron problemas durante la instalación limpia.
- **Corregido:** No fue necesario realizar correcciones adicionales.
- **Resultado:** La instalación y ejecución del proyecto se completaron satisfactoriamente en un entorno limpio.