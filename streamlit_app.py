import streamlit as st
import google.generativeai as genai

# Leemos la llave de la caja fuerte (Secrets)
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

st.title("🎨 Sonarte Core")
st.write("¡Chat inteligente conectado!")
