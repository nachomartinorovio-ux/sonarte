import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE SONARTE IA
st.set_page_config(page_title="Sonarte IA: Gestor PRO", page_icon="🤖")

# INSTRUCCIONES DE SISTEMA (Pega aquí las que usas en AI Studio)
INSTRUCCIONES = """
Eres Sonarte IA, el asistente experto de Sonarte. 
Tu misión es ayudar al gestor con dudas operativas.
Si el mensaje es un reporte (ej: 'Sierpes 1 limpieza'), confírmalo brevemente. 
Eres eficiente, resolutivo y profesional.
"""

# Configuración de seguridad para evitar el ERROR 400 (Bloquea nada)
seguridad = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

st.title("🤖 Sonarte IA: Gestor PRO")

# 2. ARRANQUE DEL MOTOR
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Buscador automático para evitar el 404
    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    motor = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in modelos else modelos[0]
    
    model = genai.GenerativeModel(
        model_name=motor,
        system_instruction=INSTRUCCIONES
    )
    
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.sidebar.success(f"🚀 Motor Activo: {motor}")
except Exception as e:
    st.error(f"Fallo crítico de arranque: {e}")
    st.stop()

# 3. INTERFAZ DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("¿Qué ha pasado hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # IA Responde al gestor
            response = model.generate_content(prompt, safety_settings=seguridad)
            texto_ia = response.text
            
            # GUARDADO PARA MAKE (ENTRADA_GLIDE)
            df_actual = conn.read(worksheet="ENTRADA_GLIDE")
            nueva_fila = pd.DataFrame([{
                "FECHA": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "MENSAJE_BRUTO": prompt # Make recibirá el mensaje original
            }])
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="ENTRADA_GLIDE", data=df_final)

            st.markdown(texto_ia)
            st.session_state.messages.append({"role": "assistant", "content": texto_ia})
            st.balloons()
            st.caption("📊 Reporte enviado a Make.")
        except Exception as e:
            st.error(f"Error en el proceso: {e}")
