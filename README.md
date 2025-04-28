# ⚡ Dashboard de Monitoreo Eléctrico - IELE

Bienvenido al **Dashboard de Monitoreo Eléctrico IELE**.  
Esta aplicación permite visualizar, analizar y configurar alarmas basadas en datos de voltajes, corrientes y factor de potencia.

---

## 📋 Descripción

El Dashboard está diseñado para ofrecer:
- Visualización interactiva de voltajes, corrientes y potencias a lo largo del día.
- Configuración dinámica de alarmas y umbrales críticos.
- Gráficos dinámicos y responsivos utilizando **Plotly**.
- Una experiencia amigable y profesional utilizando **Streamlit**.

---

## 📁 Estructura del Proyecto

```bash
streamlit-dashboard-iele/
│
├── .gitignore
├── README.md
├── requirements.txt
├── 1_Home.py
│
├── pages/
│   ├── 2_Dashboard.py
│   └── 3_Configuracion.py
│
└── utils/
    ├── config_loader.py
    └── plots.py
