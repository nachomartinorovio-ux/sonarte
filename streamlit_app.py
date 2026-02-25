import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# Configuración de la App
st.set_page_config(page_title="Sonarte IA", page_icon="🤖", layout="wide")

# Estilo visual para que se vea Pro
st.markdown("### 🤖 Sonarte IA: Gestión Inteligente")
st.divider()

# 1. Configuración de Conexiones
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# 2. Historial de Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 3. Entrada de Usuario
if prompt := st.chat_input("¿Qué ha pasado hoy en los apartamentos?"):
    # Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Sonarte IA está pensando..."):
            try:
                # La IA resume el reporte
                instrucciones = f"Resume este reporte de apartamento de forma profesional en 5 palabras: {prompt}"
                response = model.generate_content(instrucciones)
                resumen = response.text.strip()

                # ESCRIBIR EN EXCEL
                # 1. Leer datos actuales (Pestaña: ENTRADA_GLIDE)
                df_actual = conn.read(worksheet="ENTRADA_GLIDE")
                
                # 2. Crear nueva fila con fecha de hoy
                nueva_fila = pd.DataFrame([{
                    "FECHA": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "MENSAJE_BRUTO": resumen
                }])
                
                # 3. Unir y subir
                df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                conn.update(worksheet="ENTRADA_GLIDE", data=df_final)

                # Mostrar respuesta final
                respuesta_ia = f"✅ Entendido. He registrado en el Excel: **{resumen}**"
                st.write(respuesta_ia)
                st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})

            except Exception as e:
                st.error(f"Vaya, hubo un error al guardar: {e}")
