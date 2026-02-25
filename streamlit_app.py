import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# Configuración Pro
st.set_page_config(page_title="Sonarte IA", page_icon="🤖", layout="centered")
st.title("🤖 Sonarte IA: Gestión Inteligente")

# 1. Configuración de Conexiones
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Usamos 'latest' para asegurar que conecte con la versión más nueva
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de configuración inicial: {e}")
    st.stop()

# 2. Lógica del Chat
if prompt := st.chat_input("¿Qué ha pasado hoy en los apartamentos?"):
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # La IA procesa el mensaje
            instrucciones = f"Resume este reporte de apartamento en máximo 5 palabras: {prompt}"
            response = model.generate_content(instrucciones)
            resumen = response.text.strip()

            # ESCRIBIR EN EXCEL
            # Leemos la pestaña ENTRADA_GLIDE
            df_actual = conn.read(worksheet="ENTRADA_GLIDE")
            
            # Creamos la fila nueva
            nueva_fila = pd.DataFrame([{
                "FECHA": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "MENSAJE_BRUTO": resumen
            }])
            
            # Unimos y actualizamos el Google Sheet
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="ENTRADA_GLIDE", data=df_final)

            st.success(f"✅ Registrado en Excel: {resumen}")
            
        except Exception as e:
            st.error(f"Vaya, hubo un error al procesar o guardar: {e}")
            st.info("Si ves un error 404, borra la app en Streamlit Cloud y créala de nuevo.")
