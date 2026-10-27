"""Generación del resumen.txt con los resultados de las clases CSV y JSON."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any


class GeneradorResumenTxt:
    """Crea un archivo de texto que resume lo realizado con el CSV y el JSON.

    Args:
        url_csv: URL específica de origen del archivo CSV.
        url_json: URL específica de origen del archivo JSON.
    """

    def __init__(self, url_csv: str, url_json: str) -> None:
        self.url_csv = url_csv
        self.url_json = url_json

    def generar_resumen(
        self,
        resultado_csv: dict[str, Any],
        resultado_json: dict[str, Any],
        ruta_salida: str | Path = "resumen.txt",
    ) -> Path:
        """Escribe el resumen y devuelve la ruta del archivo."""
        contenido = self._construir_contenido(resultado_csv, resultado_json)
        path = Path(ruta_salida)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as archivo:
            archivo.write(contenido)
        return path

    def leer_resumen(self, ruta: str | Path = "resumen.txt") -> str:
        """Devuelve el contenido del resumen guardado."""
        with open(Path(ruta), "r", encoding="utf-8") as archivo:
            return archivo.read()

    # ------------------------------------------------------------------
    # Auxiliares
    # ------------------------------------------------------------------
    def _construir_contenido(
        self, resultado_csv: dict[str, Any], resultado_json: dict[str, Any]
    ) -> str:
        lineas = [
            "RESUMEN DE LA ACTIVIDAD AE2: MANEJO DE ARCHIVOS CSV, JSON Y TXT",
            "=" * 64,
            f"Fecha de generación: {datetime.now():%Y-%m-%d %H:%M:%S}",
            "",
            "1. URL de origen",
            f"- CSV:  {self.url_csv}",
            f"- JSON: {self.url_json}",
        ]

        for numero, resultado in ((2, resultado_csv), (3, resultado_json)):
            lineas += ["", f"{numero}. Archivo {resultado['formato']}"]
            lineas += self._seccion_archivo(resultado)

        lineas += ["", "4. Clases y métodos utilizados"]
        for resultado in (resultado_csv, resultado_json):
            metodos = ", ".join(resultado["metodos_usados"])
            lineas.append(f"- {resultado['clase']}: {metodos}")
        lineas.append(f"- {type(self).__name__}: generar_resumen, leer_resumen")

        total = resultado_csv["registros_importados"] + resultado_json["registros_importados"]
        lineas += [
            "",
            "5. Registros procesados",
            f"- CSV:  {resultado_csv['registros_importados']} importados, "
            f"{resultado_csv['registros_guardados']} guardados",
            f"- JSON: {resultado_json['registros_importados']} importados, "
            f"{resultado_json['registros_guardados']} guardados",
            f"- Total importados: {total}",
        ]
        return "\n".join(lineas) + "\n"

    @staticmethod
    def _seccion_archivo(resultado: dict[str, Any]) -> list[str]:
        lineas = [
            f"- Archivo importado: {resultado['archivo_importado']}",
            f"- Archivo nuevo guardado: {resultado['archivo_guardado']}",
            "- Modificaciones realizadas:",
        ]
        modificaciones = resultado["modificaciones"] or ["(ninguna)"]
        lineas += [f"    * {modificacion}" for modificacion in modificaciones]
        return lineas