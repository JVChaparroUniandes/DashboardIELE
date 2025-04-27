import streamlit as st




# Set page config
st.set_page_config(page_title="Configuración", layout="wide",page_icon="⚙️")
st.title("Configuración")

st.write("Aquí puedes establecer los límites para la detección de alarmas en el monitoreo eléctrico.")

# --------- Sección Voltajes ----------
with st.expander("🔋 Configuración de Alarmas de Voltaje", expanded=True):
    st.subheader("Parámetros de Voltaje")
    
    limite_superior_v = st.number_input(
        "Límite superior de voltaje (V)",
        min_value=0.0,
        max_value=1000.0,
        value=273.0,  # valor por defecto
        step=1.0
    )
    
    valor_nominal_v = st.number_input(
        "Valor nominal de voltaje (V)",
        min_value=0.0,
        max_value=1000.0,
        value=260.0,
        step=1.0
    )
    
    limite_inferior_v = st.number_input(
        "Límite inferior de voltaje (V)",
        min_value=0.0,
        max_value=1000.0,
        value=247.0,
        step=1.0
    )



    desbalance_moderado_v = st.number_input(
        "Máximo porcentaje de desbalance de voltaje en estado normal (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=1.0
    )

    desbalance_critico_v = st.number_input(
        "Máximo porcentaje de desbalance de voltaje en estado critico (%)",
        min_value=0.0,
        max_value=100.0,
        value=15.0,
        step=1.0
    )

# --------- Sección Corrientes ----------
with st.expander("⚡ Configuración de Alarmas de Corriente", expanded=True):
    st.subheader("Parámetro de Corriente")
    
    umbral_corriente = st.number_input(
        "Umbral máximo de corriente (A)",
        min_value=0.0,
        max_value=5000.0,
        value=1540.0,
        step=10.0
    )


    desbalance_moderado_i = st.number_input(
        "Porcentaje de desbalance de corriente en estado moderado (%)",
        min_value=0.0,
        max_value=100.0,
        value=10.0,
        step=1.0
    )

    desbalance_critico_i = st.number_input(
        "Porcentaje de desbalance de corriente en estado critico (%)",
        min_value=0.0,
        max_value=100.0,
        value=15.0,
        step=1.0
    )

# --------- Sección Potencia ----------
with st.expander("🔥 Configuración de Alarmas de Potencia", expanded=True):
    st.subheader("Parámetro de Potencia")
    
    umbral_factor_potencia = st.number_input(
        "Umbral mínimo de factor de potencia",
        min_value=0.0,
        max_value=1.1,
        value=0.9,
        step=0.01,
        format="%.2f"
    )

# --------- Botón para Guardar o Aplicar Configuración ----------
if st.button("💾 Guardar Configuración"):
    st.success("¡Configuración guardada correctamente!")
    
    # Podrías guardar en session_state
    st.session_state["configuracion_alarmas"] = {
        "limite_superior_v": limite_superior_v,
        "valor_nominal_v": valor_nominal_v,
        "limite_inferior_v": limite_inferior_v,
        "umbral_corriente": umbral_corriente,
        "umbral_factor_potencia": umbral_factor_potencia,
        "desbalance_moderado_v": desbalance_moderado_v,
        "desbalance_critico_v": desbalance_critico_v,
        "desbalance_moderado_i": desbalance_moderado_i,
        "desbalance_critico_i": desbalance_critico_i
    }