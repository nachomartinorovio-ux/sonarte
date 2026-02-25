import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# Configuración de Sonarte IA
st.set_page_config(page_title="Sonarte IA", page_icon="⚡", layout="centered")
st.title("⚡ Sonarte IA: Gestión Total")

# --- MOTOR DE INTELIGENCIA BLINDADO ---
try:
    # 1. Configurar API
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 2. Buscar modelos disponibles (Evita el error 404)
    modelos_en_tu_cuenta = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Elegimos el mejor: Flash > Pro > El que haya
    if 'models/gemini-1.5-flash' in modelos_en_tu_cuenta:
        seleccion = 'models/gemini-1.5-flash'
    elif 'models/gemini-1.5-pro' in modelos_en_tu_cuenta:
        seleccion = 'models/gemini-1.5-pro'
    else:
        seleccion = modelos_en_tu_cuenta[0]
        
    model = genai.GenerativeModel(seleccion)
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.sidebar.success(f"Motor activo: {seleccion}")

except Exception as e:
    st.error(f"Fallo al arrancar Sonarte IA: {e}")
    st.stop()

# --- INTERFAZ DE USUARIO ---
if prompt := st.chat_input("¿Qué ha pasado hoy en los apartamentos?"):
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # La IA procesa la información
            response = model.generate_content(f"Resume este reporte para un Excel en máximo 5 palabras: {prompt}")
            resumen = response.text.strip()
            
            # GUARDADO EN GOOGLE SHEETS
            # Leemos la pestaña ENTRADA_GLIDE
            df_actual = conn.read(worksheet="ENTRADA_GLIDE")
            
            # Preparamos la nueva fila
            nueva_fila = pd.DataFrame([{
                "FECHA": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "MENSAJE_BRUTO": resumen
            }])
            
            # Pegamos y subimos
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="ENTRADA_GLIDE", data=df_final)
            
            st.balloons()
            st.success(f"✅ Registrado con éxito: {resumen}")
            
        except Exception as e:
            st.error(f"Error en el proceso: {e}")
            st.info("Si el error persiste, limpia la caché en el menú de la derecha.")
