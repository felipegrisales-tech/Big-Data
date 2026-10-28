"""Manejo de archivos CSV con ``csv.reader`` y ``csv.writer``."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import csv


class ManejadorCSV:
    """Importa, modifica y guarda un archivo CSV.

    El primer renglón del archivo se trata como encabezado. Los registros se
    numeran desde 0 y no incluyen el encabezado.

    Args:
        delimitador: Carácter que separa las columnas del archivo.
        encoding: Codificación con la que se lee y se escribe el archivo.
    """

    def __init__(self, delimitador: str = ",", encoding: str = "utf-8") -> None:
        self.delimitador = delimitador
        self.encoding = encoding
        self.encabezado: list[str] = []
        self.registros: list[list[str]] = []
        self.ruta_original: Path | None = None
        self.ruta_guardada: Path | None = None
        self.registros_importados = 0
        self.modificaciones: list[str] = []
        self.metodos_usados: list[str] = []

    # ------------------------------------------------------------------
    # Importar
    # ------------------------------------------------------------------
    def importar_csv(self, ruta: str | Path) -> list[list[str]]:
        """Lee el CSV con ``csv.reader`` y devuelve los registros."""
        self._registrar_metodo("importar_csv")
        path = Path(ruta)
        if not path.is_file():
            raise FileNotFoundError(
                f"No se encontró el archivo CSV: {path}. "
                "Descárgalo de Hugging Face y guárdalo en esa ruta."
            )

        with open(path, "r", newline="", encoding=self.encoding) as archivo:
            filas = list(csv.reader(archivo, delimiter=self.delimitador))

        if not filas:
            raise ValueError(f"El archivo CSV está vacío: {path}")

        self.encabezado = filas[0]
        self.registros = filas[1:]
        self.ruta_original = path
        self.registros_importados = len(self.registros)
        self.modificaciones = []
        return self.registros

    # ------------------------------------------------------------------
    # Consultar
    # ------------------------------------------------------------------
    def mostrar(self, titulo: str = "", cantidad: int = 5) -> None:
        """Imprime el encabezado y los primeros registros."""
        self._registrar_metodo("mostrar")
        self._verificar_importado()
        if titulo:
            print(titulo)
        print(f"Columnas ({len(self.encabezado)}): {self.encabezado}")
        print(f"Registros: {len(self.registros)}")
        for indice, registro in enumerate(self.registros[:cantidad]):
            print(f"  [{indice}] {registro}")

    # ------------------------------------------------------------------
    # Modificar
    # ------------------------------------------------------------------
    def actualizar_valor(self, indice: int, columna: str, nuevo_valor: Any) -> str:
        """Cambia el valor de una columna en un registro y devuelve el anterior."""
        self._registrar_metodo("actualizar_valor")
        self._verificar_importado()
        self._verificar_indice(indice)
        if columna not in self.encabezado:
            raise ValueError(
                f"La columna '{columna}' no existe. Columnas: {self.encabezado}"
            )

        posicion = self.encabezado.index(columna)
        anterior = self.registros[indice][posicion]
        self.registros[indice][posicion] = str(nuevo_valor)
        self.modificaciones.append(
            f"Actualizado el registro {indice}, columna '{columna}': "
            f"'{anterior}' -> '{nuevo_valor}'"
        )
        return anterior

    def agregar_registro(self, registro: dict[str, Any] | list[Any]) -> int:
        """Agrega un registro al final y devuelve su índice.

        Acepta una lista con un valor por columna o un diccionario
        ``{columna: valor}``. Las columnas que falten quedan vacías.
        """
        self._registrar_metodo("agregar_registro")
        self._verificar_importado()
        if isinstance(registro, dict):
            desconocidas = set(registro) - set(self.encabezado)
            if desconocidas:
                raise ValueError(f"Columnas inexistentes: {sorted(desconocidas)}")
            fila = [str(registro.get(columna, "")) for columna in self.encabezado]
        else:
            if len(registro) != len(self.encabezado):
                raise ValueError(
                    f"El registro tiene {len(registro)} valores y el encabezado "
                    f"tiene {len(self.encabezado)} columnas."
                )
            fila = [str(valor) for valor in registro]

        self.registros.append(fila)
        indice = len(self.registros) - 1
        self.modificaciones.append(f"Agregado un registro nuevo en la posición {indice}")
        return indice

    def eliminar_registro(self, indice: int) -> list[str]:
        """Elimina un registro y lo devuelve."""
        self._registrar_metodo("eliminar_registro")
        self._verificar_importado()
        self._verificar_indice(indice)
        eliminado = self.registros.pop(indice)
        self.modificaciones.append(f"Eliminado el registro {indice}")
        return eliminado

    # ------------------------------------------------------------------
    # Guardar
    # ------------------------------------------------------------------
    def guardar_csv(self, ruta_salida: str | Path) -> Path:
        """Guarda el encabezado y los registros con ``csv.writer``."""
        self._registrar_metodo("guardar_csv")
        self._verificar_importado()
        path = Path(ruta_salida)
        if self.ruta_original and path.resolve() == self.ruta_original.resolve():
            raise ValueError(
                "La ruta de salida debe ser distinta de la original "
                "para conservar el archivo descargado."
            )

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding=self.encoding) as archivo:
            escritor = csv.writer(archivo, delimiter=self.delimitador)
            escritor.writerow(self.encabezado)
            escritor.writerows(self.registros)

        self.ruta_guardada = path
        return path

    # ------------------------------------------------------------------
    # Resultado para el resumen
    # ------------------------------------------------------------------
    def resultado(self) -> dict[str, Any]:
        """Devuelve los datos reales de la ejecución para el resumen."""
        return {
            "formato": "CSV",
            "clase": type(self).__name__,
            "archivo_importado": str(self.ruta_original) if self.ruta_original else None,
            "archivo_guardado": str(self.ruta_guardada) if self.ruta_guardada else None,
            "registros_importados": self.registros_importados,
            "registros_guardados": len(self.registros) if self.ruta_guardada else 0,
            "modificaciones": list(self.modificaciones),
            "metodos_usados": list(self.metodos_usados),
        }

    # ------------------------------------------------------------------
    # Auxiliares
    # ------------------------------------------------------------------
    def _registrar_metodo(self, nombre: str) -> None:
        if nombre not in self.metodos_usados:
            self.metodos_usados.append(nombre)

    def _verificar_importado(self) -> None:
        if not self.encabezado:
            raise RuntimeError("Primero importa un archivo con importar_csv().")

    def _verificar_indice(self, indice: int) -> None:
        if not 0 <= indice < len(self.registros):
            raise IndexError(
                f"Índice {indice} fuera de rango (hay {len(self.registros)} registros)."
            )
