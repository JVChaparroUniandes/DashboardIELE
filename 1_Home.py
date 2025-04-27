import streamlit as st
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(page_title="Home", layout="wide",page_icon="⚡")




with st.sidebar:
    st.title("🔌 Menú Principal")
    st.write("Navega por las diferentes secciones para acceder a herramientas especializadas.")
    st.markdown("---")

# Encabezado Principal
st.title("Calidad de la potencia")
st.write("Bienvenido al dashboard diseñado para monitorear la calidad de la potencia en su empresa. Aquí encontrará herramientas de análisis, visualización y predicción para apoyar sus proyectos.")

# Separador visual
st.markdown("---")

# Sección de Tarjetas de Información
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📊 Monitoreo en Tiempo Real")
    st.write("Cargue y analice datos de mediciones eléctricas en tiempo real.")

with col2:
    st.subheader("⚙️ Predicciones")
    st.write("Realice predicciones de su sistema de potencia que le permitan mejorar su operación.")

with col3:
    st.subheader("📡Configuración de alarmas ")
    st.write("Visualice los datos en tiempo real y genere reportes técnicos.")

# Separador visual
st.markdown("---")

# Sección de Carga de Archivos
st.subheader("📂 Cargue aquí las mediciones tomadas del analizador")
uploaded_file = st.file_uploader("Sube un archivo CSV con datos de medición", type=["csv"])

if uploaded_file is not None:

    #Convertimos el csv en un df
    df=pd.read_csv(uploaded_file)
    #Guardamos el df en st.session_state
    st.session_state.df=df
    # Mostramos el dataframe
    st.success("✅ Archivo cargado correctamente")
    # Mostrar una vista previa de los datos
    st.write("🔍 Vista previa de los datos:")
    st.dataframe(df.head())

# Mensaje final
st.info("🔍 Explore las diferentes secciones del dashboard en la barra lateral.")