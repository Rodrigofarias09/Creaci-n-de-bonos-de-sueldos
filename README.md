# 📋 Sistema de Recibos de Sueldo - Escuelas de Frontera

Un sistema web para generar automáticamente recibos de sueldo en PDF a partir de archivos Excel.

## ✨ Características

- 📊 **Carga Excel**: Sube tu archivo de remuneraciones
- 🤖 **Automático**: Genera PDFs para todos los empleados
- 💾 **Descarga ZIP**: Todos los recibos en un archivo
- 🧮 **Cálculos**: Automático de neto con descuentos legales
- 🎨 **Profesional**: Recibos formateados y listos para usar
- 📱 **Online**: Accede desde cualquier computadora

## 🚀 Inicio Rápido (Local)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar app web
streamlit run app_streamlit.py

# 3. O ejecutar versión línea de comandos
python generar_recibos.py
```

## ☁️ Despliegue Online

Para usar la app desde Internet en otra computadora, seguí la guía completa en [DEPLOY.md](DEPLOY.md)

**Recomendación:** Usá **Streamlit Cloud** (gratis y sin complicaciones)

## 📁 Estructura de Archivos

```
sistema-recibos/
├── app_streamlit.py           # App web principal
├── generar_recibos.py         # Lógica de generación de PDFs
├── requirements.txt            # Dependencias Python
├── DEPLOY.md                   # Guía de despliegue
├── README.md                   # Este archivo
├── .streamlit/
│   └── config.toml            # Configuración de Streamlit
└── .gitignore                 # Archivos a ignorar en Git
```

## 📋 Formato del Excel Esperado

El archivo Excel debe tener:
1. Una hoja llamada **"Remuneración"**
2. Encabezados en filas 6-7 (el código detecta automáticamente)
3. Columnas requeridas:
   - **Apellido y Nombre** (o similar)
   - **CUIL** (opcional)
   - **Sueldo Base** o **Básico**
   - Otras columnas de conceptos de remuneración

## 💰 Descuentos Automáticos

El sistema calcula automáticamente:
- **Jubilación**: 11%
- **Obra Social**: 3%
- **Ley 19032**: 3%

## 🛠️ Requisitos

- Python 3.7+
- pandas
- openpyxl
- fpdf2
- streamlit

## 📝 Licencia

Uso libre para escuelas y organizaciones educativas.

## ❓ Soporte

Si tienes problemas, verifica:
1. El formato del archivo Excel
2. Que todas las librerías están instaladas
3. La versión de Python (3.7 o superior)

---

**¡Espero que te sea útil! 🎓**
