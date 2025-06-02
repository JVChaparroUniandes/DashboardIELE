import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fpdf import FPDF
from datetime import datetime
import os

# ----------------------------------
# 📌 Configuración inicial
# ----------------------------------
st.set_page_config(page_title="Generar Reporte", layout="wide", page_icon="📊")

st.title("📊 Generar reporte del sistema")
st.write("En esta sección puedes generar un reporte del sistema con los datos de monitoreo y las gráficas generadas.")

TMP_DIR = "./tmp"
os.makedirs(TMP_DIR, exist_ok=True)

# ----------------------------------
# 📦 Funciones auxiliares
# ----------------------------------

def graficar_voltaje_matplotlib(df, columnas, config, nombre_archivo):
    """Crea una imagen PNG de la gráfica de voltaje usando matplotlib."""
    colores_voltaje = {
        "U1_rms_AVG": "blue",
        "U2_rms_AVG": "red",
        "U3_rms_AVG": "green",
    }

    plt.figure(figsize=(12, 5))

    for col in columnas:
        plt.plot(df["Datetime"], df[col], label=col.replace("_rms_AVG", ""), color=colores_voltaje.get(col, "black"))

    # Líneas horizontales de umbrales
    plt.axhline(config["limite_superior_v"], color="red", linestyle="--", linewidth=2, label="Límite Superior")
    plt.axhline(config["valor_nominal_v"], color="gray", linestyle="--", linewidth=2, label="Valor Nominal")
    plt.axhline(config["limite_inferior_v"], color="blue", linestyle="--", linewidth=2, label="Límite Inferior")

    plt.title("Voltajes promedio por hora")
    plt.xlabel("Hora")
    plt.ylabel("Voltaje (V)")
    plt.grid(True)
    plt.legend(loc="upper right")

    # ✅ Mostrar ticks por cada hora
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    plt.xticks(rotation=45)
    plt.tight_layout()

    path = os.path.join(TMP_DIR, nombre_archivo)
    plt.savefig(path)
    plt.close()

    return path

def graficar_corriente_matplotlib(df, columnas, corriente_nominal, nombre_archivo):
    """Crea imagen PNG de la gráfica de corriente promedio usando matplotlib."""
    colores = {
        "I1_rms_AVG": "blue",
        "I2_rms_AVG": "red",
        "I3_rms_AVG": "green",
    }

    plt.figure(figsize=(12, 5))

    for col in columnas:
        plt.plot(df["Datetime"], df[col], label=col.replace("_rms_AVG", ""), color=colores.get(col, "black"))

    # Línea horizontal para corriente nominal
    plt.axhline(corriente_nominal, color="gray", linestyle="--", linewidth=2, label="Corriente Nominal")

    plt.title("Corriente promedio por hora")
    plt.xlabel("Hora")
    plt.ylabel("Corriente (A)")
    plt.grid(True)
    plt.legend(loc="upper right")

    # Formateo eje X
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    path = os.path.join("./tmp", nombre_archivo)
    plt.savefig(path)
    plt.close()

    return path

def graficar_promedio_corriente_matplotlib(promedios, corriente_nominal, nombre_archivo):
    """Genera gráfica de barras con corriente promedio por fase + umbral."""
    
    fases = ["Fase A", "Fase B", "Fase C"]
    colores = ["blue", "red", "green"]
    
    plt.figure(figsize=(8, 6))
    barras = plt.bar(fases, promedios, color=colores)

    # Mostrar valor encima de cada barra
    for barra in barras:
        yval = barra.get_height()
        plt.text(barra.get_x() + barra.get_width() / 2, yval + 1, f"{yval:.2f}", 
                 ha='center', va='bottom', fontsize=10)

    # Línea horizontal para corriente nominal
    plt.axhline(corriente_nominal, color="orange", linestyle="-", linewidth=3, label=f"Umbral {corriente_nominal} A")

    plt.title("Corriente promedio por fase")
    plt.xlabel("Fase")
    plt.ylabel("Corriente (A)")
    plt.grid(axis='y', color='lightgray', linestyle='--')
    plt.legend()
    plt.tight_layout()

    path = os.path.join("./tmp", nombre_archivo)
    plt.savefig(path)
    plt.close()
    
    return path

def graficar_factor_potencia_matplotlib(df_potencia, umbral_factor_potencia, nombre_archivo="factor_potencia.png"):
    # Agrupar por hora y calcular promedio
    df_potencia["hour"] = df_potencia["Datetime"].dt.hour
    df_hourly = df_potencia.groupby("hour")["PF_sum_AVG"].mean().reset_index()

    # Etiquetas
    etiquetas_horas = [f"{h:02d}:00" for h in range(24)]

    # Asegurarse de tener todos los valores por hora (0 a 23)
    full_hours = pd.DataFrame({"hour": range(24)})
    df_hourly = full_hours.merge(df_hourly, on="hour", how="left").fillna(0)

    # Clasificación de estado
    df_hourly["status"] = df_hourly["PF_sum_AVG"].apply(
        lambda x: "Anormal" if x < umbral_factor_potencia or x > 1 else "Normal"
    )

    colores_estado = {
        "Normal": "blue",
        "Anormal": "red"
    }

    colores_barras = [colores_estado[estado] for estado in df_hourly["status"]]

    # Gráfico
    plt.figure(figsize=(10, 6))
    bars = plt.bar(etiquetas_horas, df_hourly["PF_sum_AVG"], color=colores_barras)

    # Valores sobre barras
    for i, bar in enumerate(bars):
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.01, f"{yval:.2f}", 
                 ha='center', va='bottom', fontsize=8)

    # Personalización
    plt.title("Promedio de factor de potencia por hora")
    plt.xlabel("Hora del día")
    plt.ylabel("Factor de Potencia")
    plt.ylim(0, 1.1)
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", color="lightgrey")

    # Leyenda manual
    from matplotlib.patches import Patch
    leyenda = [
        Patch(color="blue", label=f"Normal (≥ {umbral_factor_potencia} y ≤ 1)"),
        Patch(color="red", label=f"Anormal (< {umbral_factor_potencia} o > 1)")
    ]
    plt.legend(handles=leyenda)

    # Guardar imagen
    os.makedirs("./tmp", exist_ok=True)
    path = os.path.join("./tmp", nombre_archivo)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def generar_pdf(fig_paths, df, config_text):
    """Genera un PDF con imágenes y resumen de configuración."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Reporte del Sistema", ln=True, align='C')
    pdf.ln(10)

    intro_text="Este reporte presenta un resumen detallado del comportamiento eléctrico del sistema durante el día seleccionado. Incluye el análisis de los niveles de voltaje, corriente y factor de potencia por hora, así como los valores promedio y umbrales definidos. Su propósito es facilitar el monitoreo, identificar desviaciones de los parámetros normales y apoyar la toma de decisiones técnicas.\n\n"

    # Párrafo introductorio
    if intro_text:
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, intro_text)
        pdf.ln(5)

    # Texto introductorio para la sección de alarmas
    config_intro_text = (
        "Configuración de Alarmas del Sistema\n"
    )

    # Párrafo introductorio
    if config_intro_text:
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, config_intro_text)
        pdf.ln(5)

    # Resumen de configuración
    pdf.set_font("Arial", '', 8)
    for linea in config_text:
        pdf.cell(0, 8, linea, ln=True)
    pdf.ln(5)

    # Texto introductorio para la tabla de voltajes
    intro_tabla = (
        "Resumen por cuartiles del voltaje:\n"
    )

    # Párrafo introductorio
    if intro_tabla:
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, intro_tabla)
        pdf.ln(5)

    # Tabla de datos (máximo 20 filas)
    pdf.set_font("Courier", size=10)
    tabla = df.head(20).to_string(index=True).split('\n')
    for linea in tabla:
        pdf.cell(0, 8, linea, ln=True)

    # Texto introductorio para las gráficas
    intro_graficas= (
        "Gráficas para voltaje, corriente y factor de potencia:\n"
    )

    # Párrafo introductorio
    if intro_graficas:
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, intro_graficas)
        pdf.ln(5)

    

    

    # Imágenes
    for fig_path in fig_paths:
        if os.path.exists(fig_path):
            pdf.image(fig_path, x=10, w=190)
            pdf.ln(10)

    nombre_pdf = f"reporte_{datetime.now().strftime('%Y%m%d')}.pdf"
    path_pdf = os.path.join(TMP_DIR, nombre_pdf)
    pdf.output(path_pdf)


    return path_pdf
# ----------------------------------
# 🧠 Cargar datos y configuración
# ----------------------------------
if "df" in st.session_state and st.session_state.df is not None:
    df = st.session_state.df

    df["Time"] = df["Time"].str.replace(" a. m.", " AM").str.replace(" p. m.", " PM")
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y").dt.strftime("%d/%m/%Y")
    df["Datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"], format="%d/%m/%Y %I:%M:%S %p")

    dias_disponibles = df["Date"].unique()
    fecha_seleccionada = st.selectbox("📅 Selecciona el día a visualizar:", options=dias_disponibles)

    if "configuracion_alarmas" in st.session_state:
        config = st.session_state["configuracion_alarmas"]
        alarmas_configuradas = True
    else:
        st.warning("⚠️ No hay configuración de alarmas guardada todavía. Configúrala primero.")
        alarmas_configuradas = False

    # ----------------------------------
    # 📈 Procesar datos y generar PDF
    # ----------------------------------
    if fecha_seleccionada and alarmas_configuradas:
        df_dia = df[df["Date"] == fecha_seleccionada].copy()
        df_dia = df_dia[df_dia["Datetime"].notna()]

        columnas_a_graficar_voltaje = ["U1_rms_AVG", "U2_rms_AVG", "U3_rms_AVG"]

        df_dia["Datetime"] = pd.to_datetime(df_dia["Datetime"])

        df_voltaje_resumido = (
            df_dia.set_index("Datetime")[columnas_a_graficar_voltaje]
            .resample("1H")
            .mean()
            .reset_index()
        )

        df_corriente = df_dia.copy()  # o tu fuente de corriente
        columnas_a_graficar_corriente = ["I1_rms_AVG", "I2_rms_AVG", "I3_rms_AVG"]


        df_corriente_resumido = (
        df_corriente.set_index("Datetime")[columnas_a_graficar_corriente]
        .resample("1H")
        .mean()
        .reset_index()
        )

        

        # Calcular promedios corriente
        promedios_corriente = [
            round(df_corriente["I1_rms_AVG"].mean(), 2),
            round(df_corriente["I2_rms_AVG"].mean(), 2),
            round(df_corriente["I3_rms_AVG"].mean(), 2)
        ]

        


        # Calcular cuartiles por fase
        df_tabla_voltajes = pd.DataFrame({
            "U1": [
                round(df_dia["U1_rms_AVG"].quantile(0.99),1),
                round(df_dia["U1_rms_AVG"].quantile(0.95),1),
                round(df_dia["U1_rms_AVG"].quantile(0.90),1)
            ],
            "U2": [
                round(df_dia["U2_rms_AVG"].quantile(0.99),1),
                round(df_dia["U2_rms_AVG"].quantile(0.95),1),
                round(df_dia["U2_rms_AVG"].quantile(0.90),1)
            ],
            "U3": [
                round(df_dia["U3_rms_AVG"].quantile(0.99),1),
                round(df_dia["U3_rms_AVG"].quantile(0.95),1),
                round(df_dia["U3_rms_AVG"].quantile(0.90),1)
            ],
        }, index=["99%", "95%", "90%"])

        # Botón para generar PDF
        if st.button("📄 Generar y descargar PDF"):
            with st.spinner("Generando reporte..."):

                # Crear imagen
                img_voltaje = graficar_voltaje_matplotlib(
                    df=df_voltaje_resumido,
                    columnas=columnas_a_graficar_voltaje,
                    config=config,
                    nombre_archivo="voltaje_resumido.png"
                )

                img_corriente = graficar_corriente_matplotlib(
                df=df_corriente_resumido,
                columnas=columnas_a_graficar_corriente,
                corriente_nominal=config["umbral_corriente"],
                nombre_archivo="corriente_resumido.png"
                )

                img_promedio_corriente = graficar_promedio_corriente_matplotlib(
                    promedios=promedios_corriente,
                    corriente_nominal=config["umbral_corriente"],
                    nombre_archivo="corriente_promedio_fases.png"
                )

                img_factor_potencia = graficar_factor_potencia_matplotlib(
                    df_potencia=df_dia.copy(),
                    umbral_factor_potencia=config["umbral_factor_potencia"],
                    nombre_archivo="factor_potencia_resumido.png"
                )


                # Texto resumen
                config_text = [
                    f"Límite superior de voltaje: {config['limite_superior_v']} V",
                    f"Valor nominal de voltaje: {config['valor_nominal_v']} V",
                    f"Límite inferior de voltaje: {config['limite_inferior_v']} V",
                    f"Valor nominal de corriente: {config['umbral_corriente']} I",
                    f"Factor de potencia umbral: {config['umbral_factor_potencia']}",
                ]

                # Crear PDF
                pdf_path = generar_pdf([img_voltaje,img_corriente,img_promedio_corriente,img_factor_potencia], df_tabla_voltajes, config_text)

                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇️ Descargar reporte PDF",
                        data=f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )
