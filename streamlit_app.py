import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai
from google.generativeai.types import SafetySettingDict, HarmCategory, HarmBlockThreshold
import pandas as pd
from datetime import datetime

# Configuración de Sonarte IA
st.set_page_config(page_title="Sonarte IA", page_icon="🤖")
st.title("🤖 Sonarte IA: Gestión Imparable")

# --- 1. CONFIGURACIÓN DEL MODELO (COMO EN AI STUDIO) ---
SISTEMA_PROMPT = """Eres Sonarte IA. Ayudas al gestor con dudas y registras reportes. 
Si el mensaje es un reporte de piso (limpieza, entrada, avería), confírmalo brevemente. 
Tu tono es profesional y resolutivo."""

# Filtros de seguridad en 'BLOCK_NONE' para evitar el Error 400 por bloqueos falsos
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Buscador de motor que tanto te gustó
    modelos_disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    motor = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in modelos_disponibles else modelos_disponibles[0]
    
    # Inicializamos el modelo con todo el poder
    model = genai.GenerativeModel(
        model_name=motor,
        system_instruction=SISTEMA_PROMPT,
        safety_settings=safety_settings
    )
    
    conn = st.connection("gsheets", type=GSheetsConnection)
    st.sidebar.success(f"🚀 Motor Activo: {motor}")
except Exception as e:
    st.error(f"Fallo de motor: {e}")
    st.stop()

# --- 2. EL CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("¿Qué ha pasado hoy en los pisos?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # A. Respuesta de la IA para el Gestor
            response = model.generate_content(prompt)
            texto_ia = response.text
            
            # B. Registro para MAKE (ENTRADA_GLIDE)
            # Solo enviamos un resumen corto al Excel
            resumen_query = f"Resume este mensaje en 3 palabras para una base de datos: {prompt}"
            resumen_para_excel = model.generate_content(resumen_query).text.strip()
            
            # Sincronización con GSheets
            df_actual = conn.read(worksheet="ENTRADA_GLIDE")
            nueva_fila = pd.DataFrame([{
                "FECHA": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "MENSAJE_BRUTO": resumen_para_excel
            }])
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="ENTRADA_GLIDE", data=df_final)

            # C. Mostrar resultados
            st.markdown(texto_ia)
            st.session_state.messages.append({"role": "assistant", "content": texto_ia})
            st.caption(f"📊 Reporte guardado: {resumen_para_excel}")
            st.balloons()

        except Exception as e:
            # Si da error 400, aquí veremos exactamente por qué
            st.error(f"Error 400 detectado. Detalles: {e}")
            st.info("Revisa si el mensaje es muy largo o si la API Key en Secrets tiene comillas dobles.")
