import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai

# 1. Configuración de la IA
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Título e Interfaz
st.set_page_config(page_title="Sonarte Core", page_icon="🎨")
st.title("🎨 Sonarte Core")
st.subheader("Tu asistente inteligente de apartamentos")

# 3. El Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("¿Qué ha pasado en los apartamentos?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # La IA responde
    with st.chat_message("assistant"):
        # Prompt para que la IA sepa qué hacer
        instrucciones = f"Eres Sonarte Core. Resume este mensaje para un Excel en 5 palabras: {prompt}"
        response = model.generate_content(instrucciones)
        st.write(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

st.info("Nota: La escritura automática en Excel la activaremos en el siguiente paso.")
