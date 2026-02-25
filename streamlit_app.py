import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN DE SONARTE IA
st.set_page_config(page_title="Sonarte IA", page_icon="🤖", layout="centered")

# --- INSTRUCCIONES DE COMPORTAMIENTO (COMO EN AI STUDIO) ---
SISTEMA_PROMPT = """
Eres Sonarte IA, el asistente experto y mano derecha de los gestores de Sonarte. 
Tu misión es doble:
1. Ayudar al gestor con cualquier duda sobre la operativa de los apartamentos.
2. Procesar reportes (limpiezas, averías, entradas). 
Si el gestor te da un reporte (ej: 'Sierpes 1 limpia'), tu respuesta debe ser corta y confirmar que lo has registrado.
Actúa siempre de forma profesional, eficiente y resolutiva.
"""

st.title("🤖 Sonarte IA: Gestor PRO")

# --- CONEXIÓN BLINDADA ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Configuramos el modelo con las instrucciones de AI Studio
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=SISTEMA_PROMPT
    )
    
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Dime qué ha pasado o pregunta tus dudas..."):
    # Evitamos el error 400 limpiando el texto
    user_input = prompt.strip()
    if not user_input:
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            # 1. La IA genera la respuesta (ayuda o confirmación)
            response = model.generate_content(user_input)
            respuesta_texto = response.text
            
            # 2. LÓGICA DE GUARDADO PARA MAKE (Solo si parece un reporte)
            # Si el mensaje es corto o menciona limpieza/avería, lo mandamos al Excel
            instrucciones_resumen = f"Resume para Excel en 3 palabras: {user_input}"
            resumen_ia = model.generate_content(instrucciones_resumen).text.strip()
            
            # Escribir en ENTRADA_GLIDE
            df_actual = conn.read(worksheet="ENTRADA_GLIDE")
            nueva_fila = pd.DataFrame([{
                "FECHA": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "MENSAJE_BRUTO": resumen_ia
            }])
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="ENTRADA_GLIDE", data=df_final)

            # 3. Mostrar respuesta al gestor
            st.markdown(respuesta_texto)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
            st.caption(f"📊 Registrado para Make: {resumen_ia}")
            
        except Exception as e:
            st.error(f"Fallo en el proceso: {e}")
