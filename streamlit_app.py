import streamlit as st
import google.generativeai as genai
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
st.set_page_config(page_title="Sonarte Core", page_icon="🎨")
st.title(" Sonarte IA")
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
conn = st.connection("gsheets", type=GSheetsConnection)
if prompt := st.chat_input("¿Qué ha pasado hoy?"):
with st.chat_message("user"):
st.write(prompt)
