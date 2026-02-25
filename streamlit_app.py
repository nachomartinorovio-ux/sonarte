import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# Configuración Sonarte IA
st.set_page_config(page_title="Sonarte IA", page_icon="⚡")
st.title("⚡ Sonarte IA: Gestión Imparable")

# --- CONEXIÓN DE SEGURIDAD ---
try:
    # 1. Configurar llave
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 2. Selección automática de modelo (Evita 404)
    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    seleccion = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in modelos else modelos[0]
    
    model = genai.GenerativeModel(seleccion)
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.sidebar.success(f"Motor: {seleccion}")
except Exception as e:
    st.error(f"Error de arranque: {e}")
    st.stop()

# --- LÓGICA DE LA BESTIA ---
if prompt := st.chat_input("¿Qué ha pasado hoy?"):
    # Limpiamos el texto para evitar el Error 400 (Bad Request)
    mensaje_limpio = prompt.strip()
    
    if not mensaje_limpio:
        st.warning("Escribe algo con sentido, Nacho.")
        st.stop()

    with st.chat_message("user"):
        st.write(mensaje_limpio)

    with st.chat_message("assistant"):
        try:
            # IA Resumiendo
            response = model.generate_content(f"Resume en 4 palabras: {mensaje_limpio}")
            resumen = response.text.strip()
            
            # GUARDADO EN EXCEL (Pestaña ENTRADA_GLIDE)
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
            st.error(f"Error 400/404 detectado: {e}")
            st.info("Revisa que tu API Key no tenga espacios extra en los Secrets.")
