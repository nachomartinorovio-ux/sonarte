import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# Configuración de Bestia
st.set_page_config(page_title="Sonarte IA", page_icon="⚡", layout="wide")
st.title("⚡ Sonarte IA: Gestión Total")

# --- CONEXIÓN BLINDADA ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Buscador automático de modelos para evitar el error 404
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
    
    model = genai.GenerativeModel(model_name)
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.sidebar.success(f"🚀 Motor activo: {model_name}")
except Exception as e:
    st.error(f"Fallo en motor de arranque: {e}")
    st.stop()

# --- LÓGICA DE NEGOCIO ---
if prompt := st.chat_input("¿Qué hay de nuevo en los pisos?"):
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # IA modo experto
            contexto = "Eres el gestor de Sonarte. Resume esto para el Excel en 4 palabras clave."
            response = model.generate_content(f"{contexto} Mensaje: {prompt}")
            resumen = response.text.strip()

            # Sincronización Instantánea
            df_actual = conn.read(worksheet="ENTRADA_GLIDE")
            nueva_fila = pd.DataFrame([{
                "FECHA": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "MENSAJE_BRUTO": resumen
            }])
            
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="ENTRADA_GLIDE", data=df_final)

            st.balloons() # ¡Celebración de éxito!
            st.success(f"📊 Registro completado: {resumen}")
        except Exception as e:
            st.error(f"Error en combate: {e}")
