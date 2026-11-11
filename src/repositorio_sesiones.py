"""Persistencia local de sesiones de práctica de RhythmMentor con SQLite."""

from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
from uuid import uuid4


RUTA_DB_PREDETERMINADA = (
    Path(__file__).resolve().parents[1] / "data" / "sesiones.db"
)
CAMPOS_EDITABLES = {
    "nivel",
    "objetivo",
    "duracion_total_minutos",
    "tempo_inicial_bpm",
    "ejercicios",
}


def _ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RepositorioSesiones:
    """Crea, consulta, edita y elimina sesiones en una base SQLite local. El repositorio no solicita aprobación humana. La capa que lo invoque debe obtenerla antes de persistir una sesión y, especialmente, antes de borrarla.
    """

    def __init__(self, ruta_db: str | Path = RUTA_DB_PREDETERMINADA):
        self.ruta_db = Path(ruta_db)

    @contextmanager
    def _conexion(self):
        self.ruta_db.parent.mkdir(parents=True, exist_ok=True)
        conexion = sqlite3.connect(self.ruta_db)
        conexion.row_factory = sqlite3.Row

        try:
            conexion.execute(
                """
                CREATE TABLE IF NOT EXISTS sesiones (
                    id TEXT PRIMARY KEY,
                    creado_en TEXT NOT NULL,
                    actualizado_en TEXT NOT NULL,
                    nivel TEXT NOT NULL,
                    objetivo TEXT NOT NULL,
                    duracion_total_minutos INTEGER NOT NULL
                        CHECK (duracion_total_minutos > 0),
                    tempo_inicial_bpm INTEGER
                        CHECK (tempo_inicial_bpm IS NULL OR tempo_inicial_bpm > 0),
                    ejercicios_json TEXT NOT NULL
                )
                """
            )
            yield conexion
            conexion.commit()
        except Exception:
            conexion.rollback()
            raise
        finally:
            conexion.close()

    @staticmethod
    def _validar_y_normalizar(
        *,
        nivel: str,
        objetivo: str,
        duracion_total_minutos: int,
        tempo_inicial_bpm: int | None,
        ejercicios: list[dict],
    ) -> dict:
        if not isinstance(nivel, str) or not nivel.strip():
            raise ValueError("El nivel debe ser un texto no vacío.")

        if not isinstance(objetivo, str) or not objetivo.strip():
            raise ValueError("El objetivo debe ser un texto no vacío.")

        if type(duracion_total_minutos) is not int or duracion_total_minutos <= 0:
            raise ValueError("La duración total debe ser un entero mayor que cero.")

        if tempo_inicial_bpm is not None and (
            type(tempo_inicial_bpm) is not int or tempo_inicial_bpm <= 0
        ):
            raise ValueError("El tempo inicial debe ser un entero positivo o None.")

        if not isinstance(ejercicios, list) or not ejercicios:
            raise ValueError("Debe incluirse al menos un ejercicio.")

        ejercicios_normalizados = []
        for indice, ejercicio in enumerate(ejercicios, start=1):
            if not isinstance(ejercicio, dict):
                raise ValueError(f"El ejercicio {indice} debe ser un objeto.")

            nombre = ejercicio.get("nombre")
            instrucciones = ejercicio.get("instrucciones", "")
            duracion = ejercicio.get("duracion_minutos")
            tempo = ejercicio.get("tempo_bpm")

            if not isinstance(nombre, str) or not nombre.strip():
                raise ValueError(f"El ejercicio {indice} necesita un nombre.")

            if not isinstance(instrucciones, str):
                raise ValueError(
                    f"Las instrucciones del ejercicio {indice} deben ser texto."
                )

            if type(duracion) is not int or duracion <= 0:
                raise ValueError(
                    f"La duración del ejercicio {indice} debe ser un entero positivo."
                )

            if tempo is not None and (type(tempo) is not int or tempo <= 0):
                raise ValueError(
                    f"El tempo del ejercicio {indice} debe ser un entero positivo o None."
                )

            ejercicios_normalizados.append(
                {
                    "nombre": nombre.strip(),
                    "instrucciones": instrucciones.strip(),
                    "duracion_minutos": duracion,
                    "tempo_bpm": tempo,
                }
            )

        suma_duraciones = sum(
            ejercicio["duracion_minutos"]
            for ejercicio in ejercicios_normalizados
        )
        if suma_duraciones != duracion_total_minutos:
            raise ValueError(
                "La suma de las duraciones de los ejercicios debe coincidir "
                "con la duración total de la sesión."
            )

        return {
            "nivel": nivel.strip(),
            "objetivo": objetivo.strip(),
            "duracion_total_minutos": duracion_total_minutos,
            "tempo_inicial_bpm": tempo_inicial_bpm,
            "ejercicios": ejercicios_normalizados,
        }

    @staticmethod
    def _fila_a_dict(fila: sqlite3.Row | None) -> dict | None:
        if fila is None:
            return None

        sesion = dict(fila)
        sesion["ejercicios"] = json.loads(sesion.pop("ejercicios_json"))
        return sesion

    def guardar_sesion(
        self,
        *,
        nivel: str,
        objetivo: str,
        duracion_total_minutos: int,
        ejercicios: list[dict],
        tempo_inicial_bpm: int | None = None,
    ) -> dict:
        """Guarda una sesión ya aprobada por la capa que llama al repositorio."""
        datos = self._validar_y_normalizar(
            nivel=nivel,
            objetivo=objetivo,
            duracion_total_minutos=duracion_total_minutos,
            tempo_inicial_bpm=tempo_inicial_bpm,
            ejercicios=ejercicios,
        )
        ahora = _ahora_iso()
        sesion_id = str(uuid4())

        with self._conexion() as conexion:
            conexion.execute(
                """
                INSERT INTO sesiones (
                    id, creado_en, actualizado_en, nivel, objetivo,
                    duracion_total_minutos, tempo_inicial_bpm, ejercicios_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    sesion_id,
                    ahora,
                    ahora,
                    datos["nivel"],
                    datos["objetivo"],
                    datos["duracion_total_minutos"],
                    datos["tempo_inicial_bpm"],
                    json.dumps(datos["ejercicios"], ensure_ascii=False),
                ),
            )

        return self.obtener_sesion(sesion_id)

    def obtener_sesion(self, sesion_id: str) -> dict | None:
        """Devuelve una sesión por ID, o None si no existe."""
        with self._conexion() as conexion:
            fila = conexion.execute(
                "SELECT * FROM sesiones WHERE id = ?",
                (sesion_id,),
            ).fetchone()

        return self._fila_a_dict(fila)

    def listar_sesiones(self) -> list[dict]:
        """Devuelve las sesiones de más recientes a más antiguas."""
        with self._conexion() as conexion:
            filas = conexion.execute(
                "SELECT * FROM sesiones ORDER BY creado_en DESC, id DESC"
            ).fetchall()

        return [self._fila_a_dict(fila) for fila in filas]

    def actualizar_sesion(self, sesion_id: str, **cambios) -> dict:
        """Edita campos permitidos y vuelve a validar el plan completo."""
        if not cambios:
            raise ValueError("Indica al menos un campo para actualizar.")

        campos_desconocidos = set(cambios) - CAMPOS_EDITABLES
        if campos_desconocidos:
            raise ValueError(
                "Campos no editables: " + ", ".join(sorted(campos_desconocidos))
            )

        actual = self.obtener_sesion(sesion_id)
        if actual is None:
            raise KeyError(f"No existe una sesión con ID {sesion_id}.")

        actual.update(cambios)
        datos = self._validar_y_normalizar(
            nivel=actual["nivel"],
            objetivo=actual["objetivo"],
            duracion_total_minutos=actual["duracion_total_minutos"],
            tempo_inicial_bpm=actual["tempo_inicial_bpm"],
            ejercicios=actual["ejercicios"],
        )
        actualizado_en = _ahora_iso()

        with self._conexion() as conexion:
            resultado = conexion.execute(
                """
                UPDATE sesiones
                SET actualizado_en = ?, nivel = ?, objetivo = ?,
                    duracion_total_minutos = ?, tempo_inicial_bpm = ?,
                    ejercicios_json = ?
                WHERE id = ?
                """,
                (
                    actualizado_en,
                    datos["nivel"],
                    datos["objetivo"],
                    datos["duracion_total_minutos"],
                    datos["tempo_inicial_bpm"],
                    json.dumps(datos["ejercicios"], ensure_ascii=False),
                    sesion_id,
                ),
            )

        if resultado.rowcount == 0:
            raise KeyError(f"No existe una sesión con ID {sesion_id}.")

        return self.obtener_sesion(sesion_id)

    def eliminar_sesion(self, sesion_id: str) -> bool:
        """Elimina permanentemente una sesión.

        La herramienta o interfaz debe obtener aprobación humana antes de llamar este método. Devuelve False si el ID no existe.
        """
        with self._conexion() as conexion:
            resultado = conexion.execute(
                "DELETE FROM sesiones WHERE id = ?",
                (sesion_id,),
            )

        return resultado.rowcount > 0
