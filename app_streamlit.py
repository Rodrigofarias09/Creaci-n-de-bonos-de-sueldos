import streamlit as st
import tempfile
import zipfile
import io
from pathlib import Path
import pandas as pd
from fpdf import FPDF

# Importar funciones del script principal
from generar_recibos import (
    safe_float,
    format_money,
    calcular_neto,
    find_column,
    extract_logo_image,
    build_column_names,
    generar_pdf,
    ARCHIVO_EXCEL
)


def cargar_datos(archivo):
    if isinstance(archivo, str):
        archivo = Path(archivo)
    if not archivo.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {archivo}")

    xls = pd.ExcelFile(archivo)
    sheet_name = "Remuneración" if "Remuneración" in xls.sheet_names else xls.sheet_names[0]
    df_raw = pd.read_excel(archivo, sheet_name=sheet_name, header=None)

    column_names = build_column_names(df_raw)
    df = df_raw.iloc[7:].reset_index(drop=True)
    df.columns = column_names
    return df, sheet_name


def procesar_y_generar_zip(df, excel_path):
    """Procesa el DataFrame y genera un ZIP con todos los PDFs."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        logo_path = extract_logo_image(excel_path)

        nombre_col = find_column(df, ["apellido y nombre", "nombre", "empleado", "apellido"])
        cuil_col = find_column(df, ["cuil", "cuil.", "documento"])
        neto_col = find_column(df, ["sueldo bruto sin sac ni vac", "neto", "liquido", "liquido a cobrar", "sueldo neto"])

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

        progress_bar = st.progress(0)
        status_text = st.empty()
        count = 0

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
                basico = safe_float(fila.get(find_column(df, ["sueldo base", "basico", "sueldo basico", "haber basico"]), 0.0))
                if basico:
                    remuneraciones.append(("Sueldo Base", basico))

            if neto == 0.0 and neto_col is None:
                basico_col_found = find_column(df, ["sueldo base", "basico", "sueldo basico", "haber basico"])
                if basico_col_found:
                    basico = safe_float(fila.get(basico_col_found, 0.0))
                    if basico > 0:
                        neto, total_descuentos = calcular_neto(basico)
                        jubilacion = basico * 0.11
                        obra_social = basico * 0.03
                        ley19032 = basico * 0.03
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

            # Crear PDF en memoria
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)

            if info.get("logo_path") and info["logo_path"].exists():
                try:
                    pdf.image(str(info["logo_path"]), x=10, y=8, w=30)
                    pdf.ln(22)
                except Exception:
                    pdf.ln(8)
            else:
                pdf.ln(8)

            pdf.set_font("Arial", "B", 14)
            pdf.cell(190, 10, "RECIBO DE SUELDO", ln=True, align="C")
            pdf.ln(8)

            pdf.set_font("Arial", "", 11)
            pdf.cell(190, 8, f"Empleado: {info['nombre']}", ln=True)
            pdf.cell(190, 8, f"CUIL: {info['cuil']}", ln=True)
            pdf.ln(6)

            pdf.set_font("Arial", "B", 11)
            pdf.cell(100, 8, "Concepto", border=1)
            pdf.cell(45, 8, "Haberes", border=1)
            pdf.cell(45, 8, "Descuentos", border=1, ln=True)

            pdf.set_font("Arial", "", 11)
            total_haberes = 0.0
            total_descuentos = 0.0
            if info.get("remuneraciones"):
                for concepto, monto in info["remuneraciones"]:
                    pdf.cell(100, 8, concepto, border=1)
                    if monto >= 0:
                        pdf.cell(45, 8, format_money(monto), border=1)
                        pdf.cell(45, 8, "-", border=1, ln=True)
                        total_haberes += monto
                    else:
                        pdf.cell(45, 8, "-", border=1)
                        pdf.cell(45, 8, format_money(-monto), border=1, ln=True)
                        total_descuentos += -monto

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
            pdf.cell(190, 10, f"NETO A COBRAR: {format_money(info['neto'])}", border=1, ln=True, align="R")

            # Guardar en ZIP
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            zip_file.writestr(f"Recibo_{index + 1}_{info['nombre'][:20]}.pdf", pdf_bytes)

            count += 1
            progress = count / len(df)
            progress_bar.progress(progress)
            status_text.text(f"Procesando: {count}/{len(df)} empleados...")

        if logo_path and logo_path.exists():
            try:
                logo_path.unlink()
            except:
                pass

    zip_buffer.seek(0)
    return zip_buffer


def main():
    st.set_page_config(
        page_title="Sistema de Recibos - Escuelas de Frontera",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # CSS personalizado
    st.markdown("""
        <style>
        .main {
            padding-top: 2rem;
        }
        .stButton button {
            width: 100%;
            border-radius: 5px;
            font-size: 16px;
            padding: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("📋 Sistema de Recibos de Sueldo")
    st.subheader("Escuelas de Frontera")
    st.write("Carga un archivo Excel y genera automáticamente los recibos de sueldo en PDF.")
    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"], help="Archivo con la información de empleados y remuneraciones")

    with col2:
        st.info("💡 El archivo debe contener una hoja llamada 'Remuneración' con los datos de empleados.")

    if uploaded_file is not None:
        try:
            # Guardar archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as temp_file:
                temp_file.write(uploaded_file.read())
                temp_excel_path = Path(temp_file.name)

            # Cargar datos
            with st.spinner("Cargando datos..."):
                df, sheet_name = cargar_datos(temp_excel_path)

            st.success(f"✅ Datos cargados exitosamente")
            st.info(f"📊 Se encontraron **{len(df)}** empleados en la hoja '{sheet_name}'")

            # Mostrar preview
            with st.expander("👀 Vista previa de los datos", expanded=False):
                st.dataframe(df.head(10), use_container_width=True)

            # Botón para generar
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                if st.button("🚀 Generar todos los PDFs", use_container_width=True, type="primary"):
                    with st.spinner("Generando PDFs..."):
                        zip_buffer = procesar_y_generar_zip(df, temp_excel_path)

                    st.success("✅ PDFs generados correctamente")
                    st.download_button(
                        label="📥 Descargar Recibos (ZIP)",
                        data=zip_buffer,
                        file_name="recibos_sueldo.zip",
                        mime="application/zip",
                        use_container_width=True
                    )

            # Limpiar archivo temporal
            try:
                temp_excel_path.unlink()
            except:
                pass

        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {str(e)}")
            st.info("Asegúrate de que el archivo tenga el formato correcto y contiene una hoja llamada 'Remuneración'")

    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("📝 **Versión**: 1.0")
    with col2:
        st.caption("🔄 **Última actualización**: 2026-05-01")
    with col3:
        st.caption("💼 **Sistema de Escuelas de Frontera**")


if __name__ == "__main__":
    main()
