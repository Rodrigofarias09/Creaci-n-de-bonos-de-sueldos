from __future__ import annotations

import argparse
import csv
import datetime
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Recibo:
    nombre: str
    cedula: str
    sueldo_base: float
    bonificacion: float = 0.0
    deducciones: float = 0.0
    fecha: str = datetime.date.today().isoformat()

    @property
    def sueldo_neto(self) -> float:
        return round(self.sueldo_base + self.bonificacion - self.deducciones, 2)

    def to_text(self) -> str:
        return (
            f"Recibo de sueldo - {self.fecha}\n"
            f"----------------------------------------\n"
            f"Nombre       : {self.nombre}\n"
            f"Cédula       : {self.cedula}\n"
            f"Sueldo base  : ${self.sueldo_base:,.2f}\n"
            f"Bonificación : ${self.bonificacion:,.2f}\n"
            f"Deducciones  : ${self.deducciones:,.2f}\n"
            f"----------------------------------------\n"
            f"Sueldo neto  : ${self.sueldo_neto:,.2f}\n"
        )

    def filename(self) -> str:
        safe_name = "_".join(self.nombre.strip().split())
        return f"recibo_{safe_name}_{self.fecha}.txt"


def crear_recibo(recibo: Recibo, salida: Path) -> Path:
    salida.parent.mkdir(parents=True, exist_ok=True)
    destino = salida / recibo.filename()
    destino.write_text(recibo.to_text(), encoding="utf-8")
    return destino


def leer_csv(ruta_csv: Path) -> list[Recibo]:
    recibos: list[Recibo] = []
    with ruta_csv.open(newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            recibos.append(
                Recibo(
                    nombre=fila.get("nombre", "").strip(),
                    cedula=fila.get("cedula", "").strip(),
                    sueldo_base=float(fila.get("sueldo_base", 0)),
                    bonificacion=float(fila.get("bonificacion", 0)),
                    deducciones=float(fila.get("deducciones", 0)),
                    fecha=fila.get("fecha", datetime.date.today().isoformat()).strip() or datetime.date.today().isoformat(),
                )
            )
    return recibos


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generador de recibos de sueldo para empleado(s)."
    )
    parser.add_argument("--nombre", help="Nombre del empleado")
    parser.add_argument("--cedula", help="Cédula o documento del empleado")
    parser.add_argument("--sueldo-base", type=float, default=0.0, help="Sueldo base")
    parser.add_argument("--bonificacion", type=float, default=0.0, help="Monto de bonificación")
    parser.add_argument("--deducciones", type=float, default=0.0, help="Monto total de deducciones")
    parser.add_argument("--csv", type=Path, help="Ruta a un archivo CSV con recibos")
    parser.add_argument("--salida", type=Path, default=Path("recibos"), help="Directorio de salida para los recibos")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    recibos: list[Recibo] = []

    if args.csv:
        recibos = leer_csv(args.csv)
    else:
        if not args.nombre or not args.cedula:
            raise SystemExit("Error: debe indicar --nombre y --cedula cuando no se usa --csv.")

        recibos.append(
            Recibo(
                nombre=args.nombre,
                cedula=args.cedula,
                sueldo_base=args.sueldo_base,
                bonificacion=args.bonificacion,
                deducciones=args.deducciones,
            )
        )

    salida_dir = Path(args.salida)
    for recibo in recibos:
        archivo_creado = crear_recibo(recibo, salida_dir)
        print(f"Recibo creado: {archivo_creado}")


if __name__ == "__main__":
    main()
