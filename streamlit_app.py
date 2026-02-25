import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# Configuración básica
st.set_page_config(page_title="Sonarte IA", page_icon="🤖")
st.title("🤖 Sonarte IA")

# 1. Configuración del Motor (Instrucciones de AI Studio)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction="Eres Sonarte IA. Ayudas al gestor y registras reportes de limpieza o averías de forma breve."
    )
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.sidebar.success("🚀 Motor: Gemini 1.5 Flash")
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# 2. Historial de Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# 3. Entrada de Usuario
if prompt := st.chat_input("¿Qué ha pasado hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # Respuesta de la IA
            response = model.generate_content(prompt)
            texto_ia = response.text
            
            # Guardado para MAKE (Pestaña ENTRADA_GLIDE)
            df_actual = conn.read(worksheet="ENTRADA_GLIDE")
            nueva_fila = pd.DataFrame([{
                "FECHA": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "MENSAJE_BRUTO": prompt # Enviamos el mensaje tal cual para que Make lo procese
            }])
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="ENTRADA_GLIDE", data=df_final)

            st.write(texto_ia)
            st.session_state.messages.append({"role": "assistant", "content": texto_ia})
            st.balloons()
        except Exception as e:
            st.error(f"Error: {e}")
