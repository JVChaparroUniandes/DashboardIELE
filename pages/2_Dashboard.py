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

            fig, ax = plt.subplots(figsize=(10, 6))

            # Graficar en Seaborn sin margen de error
            sns.lineplot(data=df_voltajes, x="Datetime", y="U1_rms_AVG", ax=ax, errorbar=None, color="b", linewidth=2, label="U1")
            sns.lineplot(data=df_voltajes, x="Datetime", y="U2_rms_AVG", ax=ax, errorbar=None, color="r", linewidth=2, label="U2")
            sns.lineplot(data=df_voltajes, x="Datetime", y="U3_rms_AVG", ax=ax, errorbar=None, color="g", linewidth=2, label="U3")

            # Título y ejes
            ax.set_title("Medida del voltaje promedio", fontsize=16, fontweight="bold")
            ax.set_xlabel("Hora", fontsize=14)
            ax.set_ylabel("Voltajes L-N (V)", fontsize=14)

            # Establecer límites del eje X para evitar ticks excesivos
            x_min = df_voltajes["Datetime"].min()
            x_max = df_voltajes["Datetime"].max()
            ax.set_xlim([x_min, x_max])

            # Ticks controlados por hora
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            plt.xticks(rotation=45)

            # Línea horizontal punteada dinámica nominal
            voltaje_nominal = 260
            ax.axhline(y=voltaje_nominal, color='grey', linestyle='--', linewidth=2)
            ax.axhline(y=voltaje_nominal * 1.05, color='red', linestyle='--', linewidth=2)
            ax.axhline(y=voltaje_nominal * 0.95, color='blue', linestyle='--', linewidth=2)

            # Estética
            ax.grid(True, linestyle="--", alpha=0.6)
            ax.legend(title="Fases", loc="upper right")

            # Mostrar gráfico
            st.pyplot(fig)
            filtro_placeholder = st.empty()
        
        with desbalance_col:
            st.write("Desbalance devoltajes")
            # Obtener el valor actual del desbalance desde el DataFrame
            valor_desbalance = df_voltajes["Uunb_AVG"].mean()  # Promedio de desbalance

            # Elegir color según nivel de desbalance
            if valor_desbalance < 5:
                color = "#90EE90"  # verde claro
                texto_estado = "Normal"
            elif valor_desbalance < 10:
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
            styled_df_voltajes = df_tabla_voltajes.style.applymap(lambda x: "background-color: yellow" if x > 260*1.05 else "")
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

            # Valor del umbral
            umbral_corriente = 1540
            color_linea = "orange"

            # Filtrar y asegurar que no haya valores NaT
            df_corriente = df_corriente[df_corriente["Datetime"].notna()].copy()

            # Crear la figura
            fig, ax = plt.subplots(figsize=(10, 6))

            # Líneas para I1, I2, I3
            sns.lineplot(data=df_corriente, x="Datetime", y="I1_rms_AVG", ax=ax, errorbar=None, color="b", linewidth=2, label="I1")
            sns.lineplot(data=df_corriente, x="Datetime", y="I2_rms_AVG", ax=ax, errorbar=None, color="r", linewidth=2, label="I2")
            sns.lineplot(data=df_corriente, x="Datetime", y="I3_rms_AVG", ax=ax, errorbar=None, color="g", linewidth=2, label="I3")

            # Establecer límites válidos para el eje X
            x_min = df_corriente["Datetime"].min()
            x_max = df_corriente["Datetime"].max()
            ax.set_xlim([x_min, x_max])

            # Línea horizontal punteada dinámica
            ax.axhline(y=umbral_corriente, color=color_linea, linestyle='--', linewidth=2, label=f'Umbral: {umbral_corriente} A')

            # Personalización del gráfico
            ax.set_title("Medida de corriente promedio", fontsize=16, fontweight="bold")
            ax.set_xlabel("Hora", fontsize=14)
            ax.set_ylabel("Corriente (A)", fontsize=14)

            # Control del formato del eje X
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            plt.xticks(rotation=45)

            # Cuadrícula
            ax.grid(True, linestyle="--", alpha=0.6)

            # Leyenda sin duplicados
            handles, labels = ax.get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            ax.legend(by_label.values(), by_label.keys(), title="Fases y Umbral", loc="upper right")

            # Mostrar el gráfico
            st.pyplot(fig)

            filtro_placeholder = st.empty()
        
        with desbalance_col:
            st.write("Desbalance de corriente")

            # Obtener el valor actual del desbalance desde el DataFrame
            valor_desbalance_corriente = df_corriente["Iunb_AVG"].mean()  # Promedio de desbalance

            # Elegir color según nivel de desbalance
            if valor_desbalance_corriente < 5:
                color_desbalance_corriente = "#90EE90"  # verde claro
                texto_estado_corriente = "Normal"
            elif valor_desbalance_corriente < 10:
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

            # Nombres personalizados para el eje X
            etiquetas = ['Fase 1', 'Fase 2', 'Fase 3']
            colores = ['blue', 'red', 'green']

            # Crear figura y ejes correctamente
            fig, ax = plt.subplots(figsize=(10, 6))

            # Crear el barplot
            bars = ax.bar(etiquetas, promedios_corriente.values, color=colores)

            # Línea horizontal punteada dinámica (segura)
            umbral_corriente_2 = 1540
            color_linea_2 = "orange"
            ax.axhline(y=umbral_corriente_2, color=color_linea_2, linestyle='--', linewidth=2, label=f'Umbral: {umbral_corriente_2} A')

            # Etiquetas encima de las barras
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, f'{yval:.2f}', ha='center', va='bottom', fontsize=10)

            # Etiquetas y formato
            ax.set_title("Corriente promedio por fase", fontsize=16, fontweight="bold")
            ax.set_ylabel('Corriente (A)', fontsize=14)
            ax.set_xlabel('Fases', fontsize=14)
            ax.grid(True, axis='y', linestyle='--', alpha=0.7)

            # Leyenda con solo el umbral
            ax.legend(loc='upper right')

            # Mostrar en Streamlit
            st.pyplot(fig)


        
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
            # Agrupar por hora en un nuevo df
            df_hourly = df_potencia.groupby('hour')['PF_sum_AVG'].mean().reset_index()
            # Etiquetas tipo 00:00, 01:00, ..., 23:00
            etiquetas_horas = [f"{h:02d}:00" for h in range(24)]

            # Crear columna auxiliar de condición para colores
            df_hourly['status'] = df_hourly['PF_sum_AVG'].apply(lambda x: 'Bajo' if x < 0.9 else 'Normal')

            # Definir colores para cada categoría
            colores = {'Bajo': 'red', 'Normal': 'blue'}

            plt.figure(figsize=(10, 6))
            sns.barplot(data=df_hourly, x='hour', y='PF_sum_AVG', hue='status', palette=colores, dodge=False, legend=False)

            plt.title('Promedio de factor de potencia por Hora',fontsize=16, fontweight="bold")
            plt.xlabel('Hora del Día',fontsize=14)
            plt.ylabel('Factor de Potencia',fontsize=14)

            plt.xticks(ticks=range(24), labels=etiquetas_horas, rotation=45)
            plt.yticks(np.arange(0, 1.2, 0.05))
            plt.grid(True, axis='y', linestyle='--', alpha=0.4)
            plt.tight_layout()
            st.pyplot(plt)
    
        with indicador_col:
            # Valor del gauge (podés reemplazarlo por una variable dinámica)
            valor_actual = df_potencia['PF_sum_AVG'].mean().round(3)

            # Construcción del gauge
            import plotly.graph_objects as go

            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=valor_actual,
                delta={
                    'reference': 0.9,
                    'increasing': {'color': "green"},
                    'decreasing': {'color': "red"}
                },
                title={
                    'text': "Promedio diario del factor de potencia",
                    'font': {'size': 24}
                },
                gauge={
                    'axis': {
                        'range': [0, 1.1],
                        'dtick': 0.1,
                        'tickwidth': 1,
                        'tickcolor': "black",
                        'tick0': 0,
                        'tickmode': 'linear'
                    },
                    'bar': {
                        'color': "black",        # Aguja
                        'thickness': 0.25        # Grosor de la aguja
                    },
                    'bgcolor': "white",
                    'borderwidth': 0,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 0.8], 'color': 'red'},
                        {'range': [0.8, 0.9], 'color': 'tomato'},
                        {'range': [0.90, 1], 'color': 'lightgreen'},
                        {'range': [1, 1.1], 'color': 'tomato'}
                    ]
                    
                }
            ))

            fig.update_layout(margin=dict(l=30, r=30, t=80, b=30))


            # Mostrar el gráfico en Streamlit
            st.plotly_chart(fig)
        
    
        #with tabla_col:
             
    else:
        st.warning("⚠️ No hay datos cargados. Ve a la página de inicio y sube un archivo CSV.") 

# Separador final
st.markdown("---")