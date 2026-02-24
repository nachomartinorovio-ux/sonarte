import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
st.set_page_config(page_title="Sonarte Core", page_icon="🎨")
st.title(" Sonarte IA")
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Probamos el modelo mas moderno
    model = genai.GenerativeModel('gemini-1.5-flash')
    st.success("✅ IA Conectada")
    except Exception as e:
    st.error(f"Error de llave: {e}")
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
    st.error(f"Error con el Excel: {e}")
    if "messages" not in st.session_state:
    st.session_state.messages = []

    for message in st.session_state.messages:
    with st.chat_message(message["role"]):
    st.write(message["content"])

if prompt := st.chat_input("¿Que ha pasado hoy?"):
st.session_state.messages.append({"role": "user", "content": prompt})
with st.chat_message("user"):
st.write(prompt)
