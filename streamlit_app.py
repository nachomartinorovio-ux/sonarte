import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# 1. Configuración de la IA (Gemini)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Usamos el nombre completo y actualizado del modelo
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Error en la API Key: {e}")

# 2. Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.set_page_config(page_title="Sonarte Core", page_icon="🎨")
st.title("🎨 Sonarte Core")

# 3. Interfaz del Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("¿Qué ha pasado hoy en los pisos?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # La IA procesa el mensaje
            instrucciones = f"Resume este reporte de apartamento en máximo 5 palabras y sin puntos: {prompt}"
            response = model.generate_content(instrucciones)
            resumen = response.text.strip()
            
            # --- AQUÍ ESCRIBIMOS EN EL EXCEL ---
            # Leemos los datos actuales (Asegúrate que el nombre de la hoja coincide)
            df_actual = conn.read(worksheet="ENTRADA_GLIDE")
            
            # Creamos la nueva fila
            nueva_fila = pd.DataFrame([{
                "FECHA": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                "MENSAJE_BRUTO": resumen
            }])
            
            # Unimos los datos viejos con el nuevo y subimos al Excel
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="ENTRADA_GLIDE", data=df_final)
            
            st.success(f"✅ Registrado en Excel: {resumen}")
            st.session_state.messages.append({"role": "assistant", "content": f"He anotado: {resumen}"})
            
        except Exception as e:
            st.error(f"Vaya, ha pasado algo: {e}")
