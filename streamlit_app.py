import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# 1. Configuración de la IA con reintento
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Probamos con el nombre más genérico
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error de configuración: {e}")

# 2. Conexión con Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Error conectando con el Excel. Revisa los Secrets.")

st.set_page_config(page_title="Sonarte Core", page_icon="🎨")
st.title("🎨 Sonarte Core")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("¿Qué ha pasado hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # IA Procesando
            res = model.generate_content(f"Resume en 4 palabras: {prompt}")
            resumen = res.text.strip()
            
            # ESCRITURA EN EXCEL
            # Leemos la hoja (Asegúrate que se llama así en tu Excel)
            df_actual = conn.read(worksheet="ENTRADA_GLIDE")
            
            # Nueva fila
            nueva_fila = pd.DataFrame([{
                "FECHA": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                "MENSAJE_BRUTO": resumen
            }])
            
            # Concatenar y actualizar
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="ENTRADA_GLIDE", data=df_final)
            
            st.success(f"✅ Registrado: {resumen}")
            st.session_state.messages.append({"role": "assistant", "content": f"Anotado en el Excel: {resumen}"})
            
        except Exception as e:
            st.error(f"Error técnico: {e}")
            st.info("Prueba a darle a 'Reboot App' en el menú de la derecha.")
