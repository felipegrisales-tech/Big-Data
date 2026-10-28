"""Manejo de archivos JSON con ``json.load`` y ``json.dump``."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import json


class ManejadorJSON:
    """Importa, modifica y guarda un archivo JSON.

    Funciona con archivos cuyo contenido es una lista de objetos
    (``[{...}, {...}]``) o un objeto que contiene esa lista bajo una clave
    (``{"datos": [{...}, {...}]}``). En el segundo caso se puede indicar la
    clave con ``clave_registros``; si no se indica, se usa la primera clave
    cuyo valor sea una lista.

    Args:
        clave_registros: Clave que contiene la lista de registros, si aplica.
        encoding: Codificación con la que se lee y se escribe el archivo.
    """

    def __init__(self, clave_registros: str | None = None, encoding: str = "utf-8") -> None:
        self.clave_registros = clave_registros
        self.encoding = encoding
        self.datos: Any = None
        self.ruta_original: Path | None = None
        self.ruta_guardada: Path | None = None
        self.registros_importados = 0
        self.modificaciones: list[str] = []
        self.metodos_usados: list[str] = []

    # ------------------------------------------------------------------
    # Importar
    # ------------------------------------------------------------------
    def importar_json(self, ruta: str | Path) -> Any:
        """Lee el JSON con ``json.load`` y devuelve su contenido."""
        self._registrar_metodo("importar_json")
        path = Path(ruta)
        if not path.is_file():
            raise FileNotFoundError(
                f"No se encontró el archivo JSON: {path}. "
                "Descárgalo de Hugging Face y guárdalo en esa ruta."
            )

        with open(path, "r", encoding=self.encoding) as archivo:
            self.datos = json.load(archivo)

        self.ruta_original = path
        self.modificaciones = []
        self.registros_importados = len(self.obtener_registros())
        return self.datos

    # ------------------------------------------------------------------
    # Consultar
    # ------------------------------------------------------------------
    def obtener_registros(self) -> list[Any]:
        """Devuelve la lista de registros del archivo."""
        self._registrar_metodo("obtener_registros")
        self._verificar_importado()
        if isinstance(self.datos, list):
            return self.datos
        if isinstance(self.datos, dict):
            if self.clave_registros is not None:
                registros = self.datos.get(self.clave_registros)
                if not isinstance(registros, list):
                    raise ValueError(
                        f"La clave '{self.clave_registros}' no contiene una lista."
                    )
                return registros
            for clave, valor in self.datos.items():
                if isinstance(valor, list):
                    self.clave_registros = clave
                    return valor
        raise ValueError(
            "No se encontró una lista de registros. Indica la clave con "
            "ManejadorJSON(clave_registros='...')."
        )

    def campos(self) -> list[str]:
        """Devuelve los nombres de los campos del primer registro."""
        self._registrar_metodo("campos")
        registros = self.obtener_registros()
        if not registros or not isinstance(registros[0], dict):
            raise ValueError("Los registros del JSON deben ser objetos (diccionarios).")
        return list(registros[0].keys())

    def mostrar(self, titulo: str = "", cantidad: int = 3) -> None:
        """Imprime la cantidad de registros y los primeros registros."""
        self._registrar_metodo("mostrar")
        registros = self.obtener_registros()
        if titulo:
            print(titulo)
        print(f"Registros: {len(registros)}")
        for indice, registro in enumerate(registros[:cantidad]):
            print(f"  [{indice}] {json.dumps(registro, ensure_ascii=False)}")

    # ------------------------------------------------------------------
    # Modificar
    # ------------------------------------------------------------------
    def actualizar_valor(self, indice: int, campo: str, nuevo_valor: Any) -> Any:
        """Cambia el valor de un campo en un registro y devuelve el anterior."""
        self._registrar_metodo("actualizar_valor")
        registros = self.obtener_registros()
        self._verificar_indice(registros, indice)
        registro = registros[indice]
        if not isinstance(registro, dict):
            raise TypeError("Los registros del JSON deben ser objetos (diccionarios).")
        if campo not in registro:
            raise KeyError(f"El campo '{campo}' no existe. Campos: {list(registro)}")

        anterior = registro[campo]
        registro[campo] = nuevo_valor
        self.modificaciones.append(
            f"Actualizado el registro {indice}, campo '{campo}': "
            f"{anterior!r} -> {nuevo_valor!r}"
        )
        return anterior

    def agregar_registro(self, registro: dict[str, Any]) -> int:
        """Agrega un registro al final y devuelve su índice."""
        self._registrar_metodo("agregar_registro")
        registros = self.obtener_registros()
        if not isinstance(registro, dict):
            raise TypeError("El registro nuevo debe ser un diccionario.")
        registros.append(registro)
        indice = len(registros) - 1
        self.modificaciones.append(f"Agregado un registro nuevo en la posición {indice}")
        return indice

    def eliminar_registro(self, indice: int) -> Any:
        """Elimina un registro y lo devuelve."""
        self._registrar_metodo("eliminar_registro")
        registros = self.obtener_registros()
        self._verificar_indice(registros, indice)
        eliminado = registros.pop(indice)
        self.modificaciones.append(f"Eliminado el registro {indice}")
        return eliminado

    # ------------------------------------------------------------------
    # Guardar
    # ------------------------------------------------------------------
    def guardar_json(self, ruta_salida: str | Path, indent: int = 2) -> Path:
        """Guarda el contenido modificado con ``json.dump``."""
        self._registrar_metodo("guardar_json")
        self._verificar_importado()
        path = Path(ruta_salida)
        if self.ruta_original and path.resolve() == self.ruta_original.resolve():
            raise ValueError(
                "La ruta de salida debe ser distinta de la original "
                "para conservar el archivo descargado."
            )

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding=self.encoding) as archivo:
            json.dump(self.datos, archivo, indent=indent, ensure_ascii=False)

        self.ruta_guardada = path
        return path

    # ------------------------------------------------------------------
    # Resultado para el resumen
    # ------------------------------------------------------------------
    def resultado(self) -> dict[str, Any]:
        """Devuelve los datos reales de la ejecución para el resumen."""
        return {
            "formato": "JSON",
            "clase": type(self).__name__,
            "archivo_importado": str(self.ruta_original) if self.ruta_original else None,
            "archivo_guardado": str(self.ruta_guardada) if self.ruta_guardada else None,
            "registros_importados": self.registros_importados,
            "registros_guardados": len(self.obtener_registros()) if self.ruta_guardada else 0,
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
        if self.datos is None:
            raise RuntimeError("Primero importa un archivo con importar_json().")

    @staticmethod
    def _verificar_indice(registros: list[Any], indice: int) -> None:
        if not 0 <= indice < len(registros):
            raise IndexError(
                f"Índice {indice} fuera de rango (hay {len(registros)} registros)."
            )
