import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# CONFIGURACIÓN DE SONARTE IA
st.set_page_config(page_title="Sonarte IA: Gestor PRO", page_icon="🤖", layout="centered")

# --- INSTRUCCIONES DE COMPORTAMIENTO (COMO EN AI STUDIO) ---
SISTEMA_PROMPT = """
Eres Sonarte IA, el asistente experto de Sonarte. 
Tu misión:
1. Ayudar al gestor con dudas sobre la operativa.
2. Si el gestor reporta algo (limpieza, avería, entrada), confírmalo de forma breve.
Eres eficiente, directo y siempre estás listo para actuar.
"""

st.title("🤖 Sonarte IA: Gestor PRO")

# --- MOTOR DE INTELIGENCIA CON BUSCADOR AUTOMÁTICO ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Buscamos qué modelos tienes activos para evitar el Error 404
    modelos_vivos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    if 'models/gemini-1.5-flash' in modelos_vivos:
        motor_final = 'models/gemini-1.5-flash'
    else:
        motor_final = modelos_vivos[0]
        
    model = genai.GenerativeModel(
        model_name=motor_final,
        system_instruction=SISTEMA_PROMPT
    )
    
    # EL CHIVATO LATERAL (Para saber que todo está OK)
    st.sidebar.success(f"🚀 Motor activo: {motor_final}")
    conn = st.connection("gsheets", type=GSheetsConnection)

except Exception as e:
    st.error(f"Fallo de arranque: {e}")
    st.stop()

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Dime qué ha pasado o pregunta tus dudas..."):
    # Limpieza de texto para evitar el Error 400
    user_input = prompt.strip()
    if not user_input:
        st.stop()

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            # 1. La IA responde como en AI Studio
            response = model.generate_content(user_input)
            respuesta_texto = response.text
            
            # 2. GUARDADO PARA MAKE (ENTRADA_GLIDE)
            # Resumimos para que Make lo entienda a la primera
            resumen_ia = model.generate_content(f"Resume en 3 palabras: {user_input}").text.strip()
            
            df_actual = conn.read(worksheet="ENTRADA_GLIDE")
            nueva_fila = pd.DataFrame([{
                "FECHA": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "MENSAJE_BRUTO": resumen_ia
            }])
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="ENTRADA_GLIDE", data=df_final)

            # 3. Mostrar resultado
            st.markdown(respuesta_texto)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
            st.caption(f"📊 Registrado para Make: {resumen_ia}")
            st.balloons()
            
        except Exception as e:
            st.error(f"Error en el proceso: {e}")
