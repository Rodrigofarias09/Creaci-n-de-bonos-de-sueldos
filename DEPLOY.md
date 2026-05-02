# 📋 Sistema de Recibos de Sueldo - Guía de Despliegue Online

## ¿Cómo ejecutar localmente?

```bash
streamlit run app_streamlit.py
```

La app se abrirá en `http://localhost:8501`

---

## ☁️ OPCIÓN 1: Desplegar en Streamlit Cloud (RECOMENDADO)

### Paso 1: Subir el código a GitHub

1. Crea una cuenta en [GitHub.com](https://github.com) (gratis)
2. Crea un nuevo repositorio llamado `sistema-recibos`
3. En tu computadora, abre Git Bash (o PowerShell) en la carpeta del proyecto:
   ```bash
   git init
   git add .
   git commit -m "Sistema de recibos inicial"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/sistema-recibos.git
   git push -u origin main
   ```

### Paso 2: Desplegar en Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en "New app"
4. Selecciona:
   - **Repository**: tu-usuario/sistema-recibos
   - **Branch**: main
   - **Main file path**: app_streamlit.py
5. ¡Listo! Tu app estará en línea en pocos segundos

**Ventajas:**
- ✅ Completamente gratis
- ✅ Automático: cada cambio en GitHub se despliega al instante
- ✅ URL pública para compartir
- ✅ Sin configuración complicada

---

## ☁️ OPCIÓN 2: Desplegar en Railway.app

1. Crea cuenta en [railway.app](https://railway.app) (gratis con límite)
2. Conecta tu repositorio de GitHub
3. Railway detectará automáticamente que es un proyecto Python
4. Selecciona `app_streamlit.py` como entry point
5. ¡Desplegado!

---

## ☁️ OPCIÓN 3: Desplegar en Replit

1. Ve a [replit.com](https://replit.com)
2. Crea un nuevo Replit
3. Sube los archivos o importa desde GitHub
4. Crea un archivo `.replit`:
   ```
   run = "streamlit run app_streamlit.py --server.port 3000"
   ```
5. Haz clic en "Run"

---

## 🔗 Compartir la app

Una vez desplegada, obtendrás una URL como:
```
https://sistema-recibos-usuario.streamlit.app
```

Comparte esta URL con tus compañeros para que accedan desde cualquier computadora 📱💻

---

## 📦 Archivos necesarios para desplegar

- ✅ `app_streamlit.py` - Aplicación principal
- ✅ `generar_recibos.py` - Lógica backend
- ✅ `requirements.txt` - Dependencias
- ✅ `.streamlit/config.toml` - Configuración
- ✅ `README.md` - Este archivo

---

## 🛠️ Si necesitas hacer cambios después

Con **Streamlit Cloud**:
1. Haz cambios en tu computadora
2. Haz `git push` a GitHub
3. Streamlit Cloud se actualiza automáticamente (en ~30 segundos)

---

## ❓ Preguntas frecuentes

**¿Qué tan rápido carga?**
- Streamlit Cloud: ~5-10 segundos
- Railway: ~3-5 segundos
- Replit: ~2-3 segundos

**¿Es gratis?**
- Sí, Streamlit Cloud es 100% gratis
- Railway tiene $5 USD de crédito mensual gratis
- Replit también es gratis

**¿Puedo usar archivos Excel grandes?**
- Sí, pero Streamlit Cloud tiene límite de 100 MB por archivo
- Recomendado: máximo 50 empleados por archivo

**¿Necesito tarjeta de crédito?**
- No, Streamlit Cloud no la pide
- Railway sí, pero es solo para verificar (no cobra)

---

## 🚀 Recomendación Final

**Usa Streamlit Cloud** porque:
1. Es la forma oficial de desplegar Streamlit
2. Integración perfecta con GitHub
3. Totalmente gratis sin límites
4. Excelente rendimiento
5. Actualizaciones automáticas

¡Cualquier pregunta, avísame! 📞
