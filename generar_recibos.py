import os
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
from fpdf import FPDF

# Nombre del archivo de entrada y carpeta de salida
ARCHIVO_EXCEL = Path("Liquidacion de Sueldos Abril 12.xlsx")
CARPETA_SALIDA = Path("Recibos_Abril")
CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)


def safe_float(value):
    try:
        if pd.isna(value):
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)

        text = str(value).strip()
        if not text:
            return 0.0

        text = text.replace("$", "").replace(" ", "").replace("(", "-").replace(")", "")
        if text.count(",") > 1 and "." in text:
            text = text.replace(",", "")
        elif text.count(".") > 1 and "," in text:
            text = text.replace(".", "").replace(",", ".")
        elif "," in text and "." not in text:
            text = text.replace(",", ".")
        else:
            text = text.replace(",", "")

        return float(text)
    except Exception:
        return 0.0


def format_money(value):
    return f"$ {value:,.2f}"


def calcular_neto(basico):
    jubilacion = basico * 0.11
    obra_social = basico * 0.03
    ley19032 = basico * 0.03
    total_descuentos = jubilacion + obra_social + ley19032
    return basico - total_descuentos, total_descuentos


def find_column(df, candidates):
    lower_columns = {str(col).strip().lower(): col for col in df.columns}
    for candidate in candidates:
        candidate_lower = candidate.strip().lower()
        if candidate_lower in lower_columns:
            return lower_columns[candidate_lower]
    return None


def generar_pdf(datos, nombre_pdf, salida):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    if datos.get("logo_path") and datos["logo_path"].exists():
        try:
            pdf.image(str(datos["logo_path"]), x=10, y=8, w=30)
            pdf.ln(22)
        except Exception:
            pdf.ln(8)
    else:
        pdf.ln(8)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(190, 10, "RECIBO DE SUELDO", ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f"Empleado: {datos['nombre']}", ln=True)
    pdf.cell(190, 8, f"CUIL: {datos['cuil']}", ln=True)
    pdf.ln(6)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(100, 8, "Concepto", border=1)
    pdf.cell(45, 8, "Haberes", border=1)
    pdf.cell(45, 8, "Descuentos", border=1, ln=True)

    pdf.set_font("Arial", "", 11)
    total_haberes = 0.0
    total_descuentos = 0.0
    if datos.get("remuneraciones"):
        for concepto, monto in datos["remuneraciones"]:
            pdf.cell(100, 8, concepto, border=1)
            if monto >= 0:
                pdf.cell(45, 8, format_money(monto), border=1)
                pdf.cell(45, 8, "-", border=1, ln=True)
                total_haberes += monto
            else:
                pdf.cell(45, 8, "-", border=1)
                pdf.cell(45, 8, format_money(-monto), border=1, ln=True)
                total_descuentos += -monto
    else:
        pdf.cell(100, 8, "Sueldo Básico", border=1)
        pdf.cell(45, 8, format_money(datos.get("basico", 0.0)), border=1)
        pdf.cell(45, 8, "-", border=1, ln=True)
        total_haberes = datos.get("basico", 0.0)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(100, 8, "Total Haberes", border=1)
    pdf.cell(45, 8, format_money(total_haberes), border=1)
    pdf.cell(45, 8, "-", border=1, ln=True)
    pdf.cell(100, 8, "Total Descuentos", border=1)
    pdf.cell(45, 8, "-", border=1)
    pdf.cell(45, 8, format_money(total_descuentos), border=1, ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, f"NETO A COBRAR: {format_money(datos['neto'])}", border=1, ln=True, align="R")

    salida_path = salida / nombre_pdf
    pdf.output(str(salida_path))
    return salida_path


def extract_logo_image(archivo):
    try:
        with zipfile.ZipFile(archivo, 'r') as z:
            candidates = [name for name in z.namelist() if name.startswith('xl/media/') and name.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not candidates:
                return None
            image_name = candidates[0]
            suffix = Path(image_name).suffix
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_file.close()
            Path(temp_file.name).write_bytes(z.read(image_name))
            return Path(temp_file.name)
    except Exception:
        return None


def build_column_names(df_raw):
    header1 = [str(x).strip() if not pd.isna(x) else "" for x in df_raw.iloc[5]]
    header2 = [str(x).strip() if not pd.isna(x) else "" for x in df_raw.iloc[6]]
    column_names = []
    current_group = ""

    for index, (first, second) in enumerate(zip(header1, header2)):
        if first:
            current_group = first

        if second:
            if second.lower() in ("importe", "%") and current_group:
                label = f"{current_group} {second}"
            else:
                label = second
        else:
            label = current_group or f"Unnamed_{index}"

        if not label:
            label = f"Unnamed_{index}"

        column_names.append(label)

    return column_names


def cargar_datos(archivo):
    if not archivo.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {archivo}")

    xls = pd.ExcelFile(archivo)
    sheet_name = "Remuneración" if "Remuneración" in xls.sheet_names else xls.sheet_names[0]
    df_raw = pd.read_excel(archivo, sheet_name=sheet_name, header=None)

    column_names = build_column_names(df_raw)
    df = df_raw.iloc[7:].reset_index(drop=True)
    df.columns = column_names
    return df, sheet_name


def main():
    df, sheet_name = cargar_datos(ARCHIVO_EXCEL)
    print(f"Leyendo hoja: {sheet_name}")

    nombre_col = find_column(df, ["apellido y nombre", "nombre", "empleado", "apellido"])
    apellido_col = None  # Since it's combined
    cuil_col = find_column(df, ["cuil", "cuil.", "documento"])
    neto_col = find_column(df, ["sueldo bruto sin sac ni vac", "neto", "liquido", "liquido a cobrar", "sueldo neto"])

    if nombre_col is None and apellido_col is None:
        raise ValueError("No se encontró ninguna columna de nombre/apellido en la hoja de empleados.")

    logo_path = extract_logo_image(ARCHIVO_EXCEL)

    ignore_keys = [
        "nro. legajo",
        "apellido y nombre",
        "cuil",
        "cant. días",
        "hs",
        "$/hora",
        "días lab",
        "%",
        "porcentaje",
        "legajo",
        "fecha de ingreso",
        "sueldo neto",
    ]

    def is_ignored_column(name):
        lower = name.lower()
        return any(lower.startswith(ignore) for ignore in ignore_keys) or lower == ""

    for index, fila in df.iterrows():
        nombre = str(fila.get(nombre_col, "")).strip()
        if not nombre or nombre.lower() == "nan":
            continue

        neto = safe_float(fila.get(neto_col, float('nan')))
        remuneraciones = []

        for col in df.columns:
            nombre_col_actual = str(col).strip()
            if is_ignored_column(nombre_col_actual):
                continue

            valor = safe_float(fila.get(col, 0.0))
            if valor:
                remuneraciones.append((nombre_col_actual, valor))

        if not remuneraciones:
            basico = safe_float(fila.get(find_column(df, ["sueldo base", "basico", "sueldo basico", "haber basico"] ), 0.0))
            if basico:
                remuneraciones.append(("Sueldo Base", basico))

        if neto == 0.0 and neto_col is None:
            # Si no hay columna de neto, calcular usando básico con descuentos
            basico_col_found = find_column(df, ["sueldo base", "basico", "sueldo basico", "haber basico"])
            if basico_col_found:
                basico = safe_float(fila.get(basico_col_found, 0.0))
                if basico > 0:
                    neto, total_descuentos = calcular_neto(basico)
                    jubilacion = basico * 0.11
                    obra_social = basico * 0.03
                    ley19032 = basico * 0.03
                    # Agregar descuentos a remuneraciones si no están ya
                    if not any("jubilación" in r[0].lower() for r in remuneraciones):
                        remuneraciones.append(("Jubilación (11%)", -jubilacion))
                        remuneraciones.append(("Obra Social (3%)", -obra_social))
                        remuneraciones.append(("Ley 19032 (3%)", -ley19032))
                else:
                    neto = sum(valor for _, valor in remuneraciones)
            else:
                neto = sum(valor for _, valor in remuneraciones)

        info = {
            'nombre': nombre,
            'cuil': fila.get(cuil_col, "Sin Dato") if cuil_col is not None else "Sin Dato",
            'neto': neto,
            'remuneraciones': remuneraciones,
            'logo_path': logo_path,
        }

        nombre_archivo = f"Recibo_{index + 1}.pdf"
        generar_pdf(info, nombre_archivo, CARPETA_SALIDA)
        print(f"Generado: {nombre_archivo}")

    if logo_path is not None and logo_path.exists():
        try:
            logo_path.unlink()
        except Exception:
            pass

    print(f"\n¡Listo! Revisa la carpeta '{CARPETA_SALIDA}'.")


if __name__ == "__main__":
    main()
