BANCO_DE_PROMPT = [
    {
        "nombre": "crear_sesion_practica",
        "system_instruction": (
            "Eres RhythmMentor, un asistente especializado en enseñar batería "
            "electrónica. Diseña sesiones claras y seguras, adecuadas al nivel, "
            "objetivo y tiempo disponible. La suma de la duración de los ejercicios "
            "debe coincidir con la duración total solicitada. Responde siguiendo "
            "el esquema indicado."
        ),
        "ejemplo_usuario": (
            "Soy principiante en batería electrónica. Tengo 20 minutos y quiero "
            "mejorar la coordinación entre manos y pies. Mi tempo inicial es 60 BPM."
        ),
        "claves_esperadas": [
            "objetivo",
            "nivel",
            "duracion_minutos",
            "bpm_inicial",
            "ejercicios",
        ],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "objetivo": {"type": "STRING"},
                "nivel": {"type": "NUMBER"},
                "duracion_minutos": {"type": "NUMBER"},
                "bpm_inicial": {"type": "NUMBER"},
                "ejercicios": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "nombre": {"type": "STRING"},
                            "duracion_minutos": {"type": "NUMBER"},
                            "bpm": {"type": "NUMBER"},
                            "instrucciones": {"type": "STRING"},
                            "objetivo": {"type": "STRING"},
                        },
                        "required": [
                            "nombre",
                            "duracion_minutos",
                            "bpm",
                            "instrucciones",
                            "objetivo",
                        ],
                    },
                },
            },
            "required": [
                "objetivo",
                "nivel",
                "duracion_minutos",
                "bpm_inicial",
                "ejercicios",
            ],
        },
    },
    {
        "nombre": "proponer_ejercicio",
        "system_instruction": (
            "Eres RhythmMentor. Propón un ejercicio de batería concreto, "
            "progresivo y apropiado para el nivel indicado. Incluye instrucciones "
            "que la persona pueda seguir y criterios sencillos para evaluar su "
            "práctica. Responde siguiendo el esquema indicado."
        ),
        "ejemplo_usuario": (
            "Propón un ejercicio de 8 minutos para practicar coordinación entre "
            "mano derecha y pie derecho a 60 BPM. Mi nivel es principiante."
        ),
        "claves_esperadas": [
            "nombre",
            "objetivo",
            "nivel",
            "duracion_minutos",
            "bpm",
            "instrucciones",
            "criterios_de_evaluacion",
        ],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "nombre": {"type": "STRING"},
                "objetivo": {"type": "STRING"},
                "nivel": {"type": "NUMBER"},
                "duracion_minutos": {"type": "NUMBER"},
                "bpm": {"type": "NUMBER"},
                "instrucciones": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                },
                "criterios_de_evaluacion": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                },
            },
            "required": [
                "nombre",
                "objetivo",
                "nivel",
                "duracion_minutos",
                "bpm",
                "instrucciones",
                "criterios_de_evaluacion",
            ],
        },
    },
    {
        "nombre": "ajustar_dificultad",
        "system_instruction": (
            "Eres RhythmMentor. Ajusta la práctica a partir del desempeño que "
            "describe la persona. Recomienda un cambio gradual de tempo o "
            "complejidad, explica brevemente el motivo y evita sugerir aumentos "
            "bruscos. Responde siguiendo el esquema indicado."
        ),
        "ejemplo_usuario": (
            "Practiqué coordinación a 60 BPM durante tres sesiones. Pude completar "
            "los ejercicios sin errores en dos sesiones, pero en la última me "
            "adelanté al usar el pie izquierdo. ¿Cómo debería ajustar la próxima práctica?"
        ),
        "claves_esperadas": [
            "evaluacion",
            "recomendacion",
            "bpm_recomendado",
            "cambio_de_dificultad",
            "proximo_paso",
        ],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "evaluacion": {"type": "STRING"},
                "recomendacion": {"type": "STRING"},
                "bpm_recomendado": {"type": "NUMBER"},
                "cambio_de_dificultad": {"type": "STRING"},
                "proximo_paso": {"type": "STRING"},
            },
            "required": [
                "evaluacion",
                "recomendacion",
                "bpm_recomendado",
                "cambio_de_dificultad",
                "proximo_paso",
            ],
        },
    },
]