import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
import plotly.graph_objects as go
from datetime import time

# Set page config
st.set_page_config(page_title="Dashboard", layout="wide",page_icon="📊")

# Título del Dashboard
st.title("📊 Dashboard de Análisis Eléctrico")
st.write("Visualización de datos de voltajes, corrientes y potencia.")

# Verificar si el DataFrame está disponible en session_state
if "df" in st.session_state and st.session_state.df is not None:
    df = st.session_state.df  # Recuperar el DataFrame

    # Reemplazar "a. m." por "AM" y "p. m." por "PM" en la columna Time
    df["Time"] = df["Time"].str.replace(" a. m.", " AM").str.replace(" p. m.", " PM")

    # Convertir Date a formato datetime (suponiendo formato día/mes/año)
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y").dt.strftime("%d/%m/%Y")

    # Unir ambas columnas en una sola (Date + Time)
    df["Datetime"] = df["Date"].astype(str) + " " + df["Time"]
    df["Datetime"] = pd.to_datetime(df["Datetime"], format="%d/%m/%Y %I:%M:%S %p")

    dias_disponibles = df["Date"].unique()

    # Selección día filtrado
    fecha_seleccionada = st.selectbox("📅 Selecciona el día a visualizar:", options=dias_disponibles)

else:
    st.warning("⚠️ No hay datos cargados. Ve a la página de inicio y sube un archivo CSV.")

st.subheader("Parámetros de Alarmas")
st.write("Configura los parámetros para la detección de alarmas en el monitoreo eléctrico.")

# Verificar si existe configuración guardada
if "configuracion_alarmas" in st.session_state:
    config = st.session_state["configuracion_alarmas"]
    
    # Puedes usar los valores así:
    limite_superior_voltaje = config["limite_superior_v"]
    valor_nominal_voltaje = config["valor_nominal_v"]
    limite_inferior_voltaje = config["limite_inferior_v"]

    valor_nominal_corriente = config["umbral_corriente"]

    umbral_factor_potencia = config["umbral_factor_potencia"]
    desbalance_moderado_v = config["desbalance_moderado_v"]
    desbalance_critico_v = config["desbalance_critico_v"]
    desbalance_moderado_i = config["desbalance_moderado_i"]
    desbalance_critico_i = config["desbalance_critico_i"]

    # Ahora puedes usarlos en tus gráficos, alertas, lógicas, etc.
    st.write(f"⚡ Límite superior voltaje: {limite_superior_voltaje} V")
    st.write(f"⚡ Límite inferior voltaje: {limite_inferior_voltaje} V")
    st.write(f"⚡ Valor nominal voltaje: {valor_nominal_voltaje} V")
    st.write(f"🔥 Umbral corriente: {valor_nominal_corriente} A")
    st.write(f"🔥 Umbral factor potencia: {umbral_factor_potencia}")

else:
    st.warning("⚠️ No hay configuración de alarmas guardada todavía. Configúrala primero.")



# Separador visual
st.markdown("---")

### 🔋 Sección de Voltajes

with st.container():
    st.subheader("Voltajes")
    if "df" in st.session_state and st.session_state.df is not None:

        
        # Primera fila (Filtro + Tabla + Indicador)
        filtro_col, desbalance_col,tabla_col = st.columns([1, 0.5,1])
        
        with filtro_col:
            
            # Crear la figura y los ejes
            df_voltajes = df[df["Date"] == fecha_seleccionada].copy()
            df_voltajes = df_voltajes[df_voltajes["Datetime"].notna()]  # Evita NaT en eje X

            # Variables que controlan las líneas horizontales
            limite_superior_voltaje = 273  # Var1
            valor_nominal_voltaje = 260    # Var2
            limite_inferior_voltaje = 247  # Var3

            # Lista de columnas que quieres graficar
            columnas_a_graficar = ["U1_rms_AVG", "U2_rms_AVG", "U3_rms_AVG"]

            # Colores personalizados para cada línea
            colores_voltaje = {
                "U1_rms_AVG": "blue",
                "U2_rms_AVG": "red",
                "U3_rms_AVG": "green",
            }

            # Crear figura
            fig_voltaje = go.Figure()

            # Añadir una línea por cada columna
            for columna in columnas_a_graficar:
                fig_voltaje.add_trace(go.Scatter(
                    x=df_voltajes["Datetime"],
                    y=df_voltajes[columna],
                    mode='lines',
                    name=columna.replace("_rms_AVG", ""),  # Opcional: limpia el nombre para mostrar bonito
                    line=dict(color=colores_voltaje.get(columna, 'black'), width=2)
                ))
            # Añadir las tres líneas horizontales
            fig_voltaje.update_layout(
                shapes=[
                    dict(type="line", xref="paper", x0=0, x1=1, yref="y", y0=limite_superior_voltaje, y1=limite_superior_voltaje,
                        line=dict(color="red", width=4, dash="dash")),
                    dict(type="line", xref="paper", x0=0, x1=1, yref="y", y0=valor_nominal_voltaje, y1=valor_nominal_voltaje,
                        line=dict(color="grey", width=4, dash="dash")),
                    dict(type="line", xref="paper", x0=0, x1=1, yref="y", y0=limite_inferior_voltaje, y1=limite_inferior_voltaje,
                        line=dict(color="blue", width=4, dash="dash")),
                ],
                annotations=[
                    dict(
                        x=1.005, y=limite_superior_voltaje,
                        xref='paper', yref='y',
                        text='Límite Superior',
                        showarrow=False,
                        font=dict(color="red", size=12),
                        xanchor='left'
                    ),
                    dict(
                        x=1.005, y=valor_nominal_voltaje,
                        xref='paper', yref='y',
                        text='Valor Nominal',
                        showarrow=False,
                        font=dict(color="grey", size=12),
                        xanchor='left'
                    ),
                    dict(
                        x=1.005, y=limite_inferior_voltaje,
                        xref='paper', yref='y',
                        text='Límite Inferior',
                        showarrow=False,
                        font=dict(color="blue", size=12),
                        xanchor='left'
                    ),
                ]
            )

            # Configurar el layout (títulos, ejes, grid, etc.)
            fig_voltaje.update_layout(
                title="Gráfica Voltaje Promedio",
                xaxis_title="Fecha y Hora",
                yaxis_title="Voltaje (V)",
                xaxis=dict(
                    tickformat="%H:%M",
                    tickmode="auto",
                    nticks=24,  # Aproximadamente 1 tick por hora si es un día
                    showgrid=True,
                    gridcolor="lightgrey",
                    tickangle=45  # Rotar las etiquetas
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="lightgrey"
                ),
                legend=dict(
                    title="Medidas",
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=40, r=120, t=80, b=40),
                height=600,
                template="simple_white"
            )

            # Mostrar en Streamlit o en notebook
            # Para Streamlit:
            st.plotly_chart(fig_voltaje, use_container_width=True)
            filtro_placeholder = st.empty()
        
        with desbalance_col:
            st.write("Desbalance de voltajes")
            # Obtener el valor actual del desbalance desde el DataFrame
            valor_desbalance = df_voltajes["Uunb_AVG"].mean()  # Promedio de desbalance

            # Elegir color según nivel de desbalance
            if valor_desbalance < desbalance_moderado_v:
                color = "#90EE90"  # verde claro
                texto_estado = "Normal"
            elif valor_desbalance < desbalance_critico_v:
                color = "#FFD700"  # dorado
                texto_estado = "Moderado"
            else:
                color = "#FF6347"  # rojo tomate
                texto_estado = "Crítico"

            # Tarjeta con estilo personalizado
            st.markdown(f"""
            <div style='
                background-color:{color};
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            '>
                <h3 style='color: black; margin-bottom: 10px;'>Desbalance Actual</h3>
                <h1 style='color: black; margin: 0;'>{valor_desbalance:.3f}%</h1>
                <p style='color: black; margin-top: 10px; font-weight: bold;'>{texto_estado}</p>
            </div>
            """, unsafe_allow_html=True)


    
        with tabla_col:

            

            # Cuartiles U1_AVG
            Q1_U1_99 = df_voltajes["U1_rms_AVG"].quantile(0.99)
            Q1_U1_95 = df_voltajes["U1_rms_AVG"].quantile(0.95)
            Q1_U1_90 = df_voltajes["U1_rms_AVG"].quantile(0.90)

            

            # Cuartiles U2_AVG
            Q1_U2_99 = df_voltajes["U2_rms_AVG"].quantile(0.99)
            Q1_U2_95 = df_voltajes["U2_rms_AVG"].quantile(0.95)
            Q1_U2_90 = df_voltajes["U2_rms_AVG"].quantile(0.90)

            
            # Cuartiles U3_AVG
            Q1_U3_99 = df_voltajes["U3_rms_AVG"].quantile(0.99)
            Q1_U3_95 = df_voltajes["U3_rms_AVG"].quantile(0.95)
            Q1_U3_90 = df_voltajes["U3_rms_AVG"].quantile(0.90)

            

            

            st.write("Cuartiles voltajes promedio RMS L-N para el día seleccionado")
            df_tabla_voltajes = pd.DataFrame({
                "U1": [Q1_U1_99,Q1_U1_95,Q1_U1_90],
                "U2": [Q1_U2_99,Q1_U2_95,Q1_U2_90],
                "U3": [Q1_U3_99,Q1_U3_95,Q1_U3_90],
            }, index=["99%","95%","90%"])

            # Estilizar la tabla para resaltar valores mayores a 260 V
            styled_df_voltajes = df_tabla_voltajes.style.applymap(lambda x: "background-color: yellow" if x > limite_superior_voltaje else "")
            # Mostrar la tabla estilizada
            st.dataframe(styled_df_voltajes)

            
            
           
            
            
    else:
        st.warning("⚠️ No hay datos cargados. Ve a la página de inicio y sube un archivo CSV.")

# Separador
st.markdown("---")

### ⚡ Sección de Corrientes
with st.container():
    st.subheader("Corriente")
    if "df" in st.session_state and st.session_state.df is not None:
        

        # Filtrar el DataFrame por la fecha seleccionada en el selectbox para corriente
        df_corriente=df[df["Date"]==fecha_seleccionada]

        # Segunda fila (Filtro + Tabla + Indicador)
        tendencia_col, desbalance_col,promedio_col = st.columns([1,0.5,1])
    
        with tendencia_col:

            


            # Lista de columnas que quieres graficar
            columnas_a_graficar_corriente = ["I1_rms_AVG", "I2_rms_AVG", "I3_rms_AVG"]

            # Colores personalizados para cada línea
            colores = {
                "I1_rms_AVG": "blue",
                "I2_rms_AVG": "red",
                "I3_rms_AVG": "green",
            }

            # Crear figura
            fig_corriente = go.Figure()

            # Añadir una línea por cada columna
            for columna in columnas_a_graficar_corriente:
                fig_corriente.add_trace(go.Scatter(
                    x=df_corriente["Datetime"],
                    y=df_corriente[columna],
                    mode='lines',
                    name=columna.replace("_rms_AVG", ""),  # Opcional: limpia el nombre para mostrar bonito
                    line=dict(color=colores.get(columna, 'black'), width=2)
                ))
            # Añadir las tres líneas horizontales
            fig_corriente.update_layout(
                shapes=[
                    
                    dict(type="line", xref="paper", x0=0, x1=1, yref="y", y0=valor_nominal_corriente, y1=valor_nominal_corriente,
                        line=dict(color="grey", width=4, dash="dash"))
                    
                ],
                annotations=[
                    
                    dict(
                        x=1.005, y=valor_nominal_corriente,
                        xref='paper', yref='y',
                        text='Corriente Nominal',
                        showarrow=False,
                        font=dict(color="grey", size=12),
                        xanchor='left'
                    )
                ]
            )

            # Configurar el layout (títulos, ejes, grid, etc.)
            fig_corriente.update_layout(
                title="Gráfica corriente promedio",
                xaxis_title="Fecha y Hora",
                yaxis_title="Corriente (A)",
                xaxis=dict(
                    tickformat="%H:%M",
                    tickmode="auto",
                    nticks=24,  # Aproximadamente 1 tick por hora si es un día
                    showgrid=True,
                    gridcolor="lightgrey",
                    tickangle=45  # Rotar las etiquetas
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="lightgrey"
                ),
                legend=dict(
                    title="Medidas",
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                margin=dict(l=40, r=120, t=80, b=40),
                height=600,
                template="simple_white"
            )

            # Mostrar en Streamlit o en notebook
            # Para Streamlit:
            st.plotly_chart(fig_corriente, use_container_width=True)

            filtro_placeholder = st.empty()
        
        with desbalance_col:
            st.write("Desbalance de corriente")

            # Obtener el valor actual del desbalance desde el DataFrame
            valor_desbalance_corriente = df_corriente["Iunb_AVG"].mean()  # Promedio de desbalance

            # Elegir color según nivel de desbalance
            if valor_desbalance_corriente < desbalance_moderado_i:
                color_desbalance_corriente = "#90EE90"  # verde claro
                texto_estado_corriente = "Normal"
            elif valor_desbalance_corriente < desbalance_critico_i:
                color_desbalance_corriente= "#FFD700"  # dorado
                texto_estado_corriente = "Moderado"
            else:
                color_desbalance_corriente = "#FF6347"  # rojo tomate
                texto_estado_corriente = "Crítico"

            # Tarjeta con estilo personalizado
            st.markdown(f"""
            <div style='
                background-color:{color_desbalance_corriente};
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            '>
                <h3 style='color: black; margin-bottom: 10px;'>Desbalance Actual</h3>
                <h1 style='color: black; margin: 0;'>{valor_desbalance_corriente:.3f}%</h1>
                <p style='color: black; margin-top: 10px; font-weight: bold;'>{texto_estado_corriente}</p>
            </div>
            """, unsafe_allow_html=True)

        with promedio_col:
            # Calcular promedios
            promedios_corriente = df_corriente[["I1_rms_AVG", "I2_rms_AVG", "I3_rms_AVG"]].mean()

           # Datos de ejemplo (reemplazar con los datos reales)
            fases_corrientes_promedio = ["Fase A", "Fase B", "Fase C"]
            corrientes = [round(df_corriente["I1_rms_AVG"].mean(),2), round(df_corriente["I2_rms_AVG"].mean(),2), round(df_corriente["I3_rms_AVG"].mean(),2)]  # valores promedio por fase (en A)
            valor_nominal_corriente = 1400  # valor nominal de corriente (en A)
            

            fig_promedio_corriente = go.Figure()  # crear figura vacía

            # Añadir barras para cada fase
            fig_promedio_corriente.add_trace(go.Bar(
                x=fases_corrientes_promedio, 
                y=corrientes,
                text=corrientes,               # mostrar los valores sobre cada barra
                textposition='outside',        # posición del texto por encima (fuera) de la barra
                marker_color=["blue", "red", "green"],  # colores para cada barra
                name="Corriente por fase", 
                showlegend=False              # no mostrar este trace en la leyenda
            ))

            # Línea visual
            fig_promedio_corriente.update_layout(
                shapes=[
                    dict(
                        type="line",
                        xref="paper", x0=0, x1=1,
                        yref="y", y0=valor_nominal_corriente, y1=valor_nominal_corriente,
                        line=dict(color="orange", width=5, dash="solid")
                    )
                ]
            )

            # Dummy trace para la leyenda
            fig_promedio_corriente.add_trace(go.Scatter(
                x=[None],
                y=[None],
                mode="lines",
                name=f"Umbral {valor_nominal_corriente} A",
                line=dict(color="orange", width=5, dash="solid")
            ))

            fig_promedio_corriente.update_layout(
                title_text="Corriente promedio por fase",
                xaxis_title="Fase",
                yaxis_title="Corriente (A)",
                yaxis=dict(showgrid=True, gridcolor="lightgray", gridwidth=1),
                margin=dict(l=40, r=120, t=80, b=40),
                height=600,
                template="simple_white"
            )

            # Mostrar en Streamlit o en notebook
            # Para Streamlit:
            st.plotly_chart(fig_promedio_corriente, use_container_width=True)


        
    else:
        st.warning("⚠️ No hay datos cargados. Ve a la página de inicio y sube un archivo CSV.")
    

# Separador
st.markdown("---")

### 🔥 Sección de Potencia
with st.container():
    st.subheader("Potencia")
    if "df" in st.session_state and st.session_state.df is not None:
        # Filtrar el DataFrame por la fecha seleccionada en el selectbox para potencia
        df_potencia=df[df["Date"]==fecha_seleccionada]
        #Modificamos la columna Time para ajustarla en fomrato datetime
        df_potencia['Time'] = pd.to_datetime(df_potencia['Time'],format='%I:%M:%S %p').dt.time
        # Extraer la hora como número (0 a 23)
        df_potencia['hour'] = pd.to_datetime(df_potencia['Time'].astype(str)).dt.hour

        
        # Tercera fila (Histograma + Indicador + Tabla)
        grafica_col, indicador_col = st.columns([1, 1])
    
        with grafica_col:
           # Agrupar por hora y calcular promedio
            df_hourly = df_potencia.groupby('hour')['PF_sum_AVG'].mean().reset_index()

            # Crear etiquetas tipo 00:00, 01:00, ..., 23:00
            etiquetas_horas = [f"{h:02d}:00" for h in range(24)]

            # Clasificar estado por nivel de PF
            df_hourly['status'] = df_hourly['PF_sum_AVG'].apply(lambda x: 'Anormal' if x < umbral_factor_potencia or x >1 else 'Normal')

            # Definir colores
            colores_estado = {
                'Anormal': 'red',
                'Normal': 'blue'
            }

            # Mapeo de colores individuales para cada barra
            colores_barras = [colores_estado[estado] for estado in df_hourly['status']]

            # Crear figura
            fig = go.Figure()

            # Añadir las barras principales
            fig.add_trace(go.Bar(
                x=etiquetas_horas,
                y=df_hourly['PF_sum_AVG'],
                marker_color=colores_barras,
                text=[f"{y:.3f}" for y in df_hourly['PF_sum_AVG']],
                textposition='outside',
                showlegend=False  # Las barras no deben aparecer en leyenda
            ))

            # ------ AGREGAR LEYENDA MANUAL ------
            fig.add_trace(go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=10, color='blue'),
                legendgroup="Normal",
                showlegend=True,
                name=f"Normal (≥ {umbral_factor_potencia} y ≤ 1)"
            ))
            fig.add_trace(go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=10, color='red'),
                legendgroup="Anormal",
                showlegend=True,
                name=f"Anormal (< {umbral_factor_potencia} o > 1)"
            ))
            # -------------------------------------

            # Layout general
            fig.update_layout(
                title="Promedio de factor de potencia por Hora",
                xaxis_title="Hora del Día",
                yaxis_title="Factor de Potencia",
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(24)),
                    ticktext=etiquetas_horas,
                    tickangle=45
                ),
                yaxis=dict(
                    range=[0, 1.1],
                    tick0=0,
                    dtick=0.05,
                    showgrid=True,
                    gridcolor="lightgrey"
                ),
                legend=dict(
                    title="Estado del PF",
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                height=600,
                template="simple_white",
                margin=dict(l=40, r=40, t=80, b=40)
            )

            # Mostrar en Streamlit
            st.plotly_chart(fig, use_container_width=True)


    
        with indicador_col:
            # Valor dinámico del gauge
            valor_actual = df_potencia['PF_sum_AVG'].mean().round(3)

            # Interpretación del valor
            if umbral_factor_potencia <= valor_actual <= 1.0:
                estado_texto = "✅ Estado: Normal"
                color_estado = "green"
            else:
                estado_texto = "⚠️ Estado: Crítico"
                color_estado = "red"

            # Crear figura del gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=valor_actual,
                title={
                    'text': "Promedio diario del factor de potencia",
                    'font': {'size': 24}
                },
                gauge={
                    'axis': {
                        'range': [0, 1.1],
                        'tickmode': 'linear',
                        'tick0': 0,
                        'dtick': 0.1,
                        'tickwidth': 1,
                        'tickcolor': "black"
                    },
                    'bar': {
                        'color': "black",
                        'thickness': 0.15    # 🔥 Hacemos la barra muy delgada (parece aguja real)
                    },
                    'bgcolor': "white",
                    'borderwidth': 1,
                    'bordercolor': "lightgrey",
                    'steps': [
                        {'range': [0, umbral_factor_potencia], 'color': '#FF4C4C'},    # rojo
                        {'range': [umbral_factor_potencia, 1.0], 'color': '#4CAF50'},  # verde
                        {'range': [1.0, 1.1], 'color': '#FF4C4C'}   # rojo
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': valor_actual
                    }
                }
            ))

            fig.update_layout(
                margin=dict(l=30, r=30, t=80, b=30),
                height=400
            )

            # Mostrar el gauge en Streamlit
            st.plotly_chart(fig, use_container_width=True)

            # Mostrar el mini-texto interpretativo
            st.markdown(f"<h4 style='text-align: center; color:{color_estado};'>{estado_texto}</h4>", unsafe_allow_html=True)
        
 
             
    else:
        st.warning("⚠️ No hay datos cargados. Ve a la página de inicio y sube un archivo CSV.") 

# Separador final
st.markdown("---")