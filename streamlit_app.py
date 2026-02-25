import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# Configuración de Sonarte IA
st.set_page_config(page_title="Sonarte IA", page_icon="⚡", layout="centered")
st.title("⚡ Sonarte IA: Gestión Total")

# --- MOTOR DE INTELIGENCIA AUTORREPARABLE ---
try:
    # 1. Conectamos con tu llave
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 2. Buscamos qué modelos tienes activos (Evita errores 404 y 400)
    modelos_vivos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Prioridad: 1.5-flash (el más rápido), si no el que sea
    if 'models/gemini-1.5-flash' in modelos_vivos:
        motor_final = 'models/gemini-1.5-flash'
    else:
        motor_final = modelos_vivos[0]
        
    model = genai.GenerativeModel(motor_final)
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.sidebar.success(f"🚀 Motor Activo: {motor_final}")

except Exception as e:
    st.error(f"Fallo de arranque: {e}")
    st.stop()

# --- CHAT PROFESIONAL ---
if prompt := st.chat_input("¿Qué ha pasado hoy en los apartamentos?"):
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # La IA resume con instrucciones claras
            contexto = "Resume este reporte de limpieza/mantenimiento en máximo 5 palabras."
            response = model.generate_content(f"{contexto} Reporte: {prompt}")
            resumen = response.text.strip()
            
            # GUARDADO EN GOOGLE SHEETS (Sincronización Total)
            df_actual = conn.read(worksheet="ENTRADA_GLIDE")
            
            # Nueva línea con la hora de España
            nueva_fila = pd.DataFrame([{
                "FECHA": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "MENSAJE_BRUTO": resumen
            }])
            
            # Unir datos y subir
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="ENTRADA_GLIDE", data=df_final)
            
            st.balloons() # ¡Celebración de éxito!
            st.success(f"✅ Registrado en Excel: {resumen}")
            
        except Exception as e:
            st.error(f"Error en combate: {e}")
            st.info("Prueba a escribir de nuevo o revisa los permisos del Excel.")
