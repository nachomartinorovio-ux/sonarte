import streamlit as st
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai

# 1. Conexión con Gemini
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Usamos gemini-1.5-flash que es el más rápido
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Revisa tu API Key en los Secrets de Streamlit.")

# 2. Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.set_page_config(page_title="Sonarte Core", page_icon="🎨")
st.title("🎨 Sonarte Core")

# 3. Interfaz del Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("¿Qué ha pasado hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # La IA resume el mensaje
            instrucciones = f"Resume este reporte de apartamento en máximo 6 palabras: {prompt}"
            response = model.generate_content(instrucciones)
            resumen = response.text
            
            # ESCRIBIR EN EL EXCEL (Aquí ocurre la magia)
            # Leemos los datos actuales
            df_actual = conn.read(worksheet="ENTRADA_GLIDE")
            # Creamos la nueva fila
            nueva_fila = {"FECHA": st.datetime.now().strftime("%d/%m/%Y %H:%M"), "MENSAJE_BRUTO": resumen}
            # La añadimos y subimos al Excel
            df_final = df_actual.append(nueva_fila, ignore_index=True)
            conn.update(worksheet="ENTRADA_GLIDE", data=df_final)
            
            st.success(f"Registrado: {resumen}")
            st.session_state.messages.append({"role": "assistant", "content": resumen})
        except Exception as e:
            st.error(f"Error al procesar: {e}")
