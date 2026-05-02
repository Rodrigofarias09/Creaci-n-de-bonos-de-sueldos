# Creación de bonos de sueldos

Proyecto simple para generar recibos de sueldo y bonificaciones.

## Estructura

- `python/generar_recibos.py`: script para generar recibos de sueldo.
- `recibos/`: directorio de salida donde se guardan los recibos generados.

## Uso

Ejecutar el script con datos individuales:

```bash
python/generar_recibos.py --nombre "Juan Pérez" --cedula "12345678" --sueldo-base 1200 --bonificacion 150 --deducciones 50
```

O usar un archivo CSV con esta estructura:

```csv
nombre,cedula,sueldo_base,bonificacion,deducciones,fecha
Juan Pérez,12345678,1200,150,50,2026-05-02
María López,87654321,1400,200,100,2026-05-02
```

Ejecutar con CSV:

```bash
python/python generar_recibos.py --csv datos_recibos.csv --salida recibos
```

Los recibos generados se guardan en la carpeta `recibos/`.
