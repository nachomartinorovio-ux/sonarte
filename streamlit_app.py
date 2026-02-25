import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# Configuración de Sonarte IA
st.set_page_config(page_title="Sonarte IA", page_icon="⚡")
st.title("⚡ Sonarte IA: Gestión Total")

# 1. MOTOR DE INTELIGENCIA
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Intentamos el más rápido, si no, el primero que funcione
    model = genai.GenerativeModel('gemini-1.5-flash')
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de arranque: {e}")
    st.stop()

# 2. INTERFAZ DE CHAT
if prompt := st.chat_input("¿Qué ha pasado hoy?"):
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # La IA resume
            response = model.generate_content(f"Resume en 4 palabras para un Excel: {prompt}")
            resumen = response.text.strip()
            
            # GUARDADO AUTOMÁTICO
            df_actual = conn.read(worksheet="ENTRADA_GLIDE")
            nueva_fila = pd.DataFrame([{
                "FECHA": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "MENSAJE_BRUTO": resumen
            }])
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="ENTRADA_GLIDE", data=df_final)
            
            st.balloons()
            st.success(f"✅ Registrado: {resumen}")
        except Exception as e:
            st.error(f"Aviso: Si ves un error 404, dale a 'Reboot' en el menú de la derecha.")
            st.info(f"Detalle técnico: {e}")
