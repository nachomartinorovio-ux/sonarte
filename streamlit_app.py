
import streamlit as st

st.title("🎨 Sonarte Core")
st.write("¡Hola Nacho! Si ves esto, tu app funciona.")

texto = st.chat_input("Escribe algo aquí...")
if texto:
    st.write(f"Has dicho: {texto}")
