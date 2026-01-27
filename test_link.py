import streamlit as st
from utils.data_manager import conectar_sheets

st.title("🚀 Prueba de Vínculo Google Sheets")

try:
    ss = conectar_sheets()
    if ss:
        st.success(f"✅ VÍNCULO EXITOSO: Conectado a '{ss.title}'")
        st.write("Hojas encontradas:", [ws.title for ws in ss.worksheets()])
    else:
        st.error("❌ FALLO DE VÍNCULO: conectar_sheets() devolvió None. Revisa tus Secrets.")
except Exception as e:
    st.error(f"❌ ERROR DE CONEXIÓN: {e}")
