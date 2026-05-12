import streamlit as st

import streamlit as st

# Refinamiento Estético: Bloomberg Moderno
st.markdown("""
    <style>
    /* Fondo principal: Gris carbón profesional */
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Títulos en blanco para mayor legibilidad */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 600;
    }

    /* Sidebar más integrada */
    [data-testid="stSidebar"] {
        background-color: #1A1A1A;
        border-right: 1px solid #333333;
    }
    
    /* Métricas: Valores en Ámbar/Oro (Clásico Bloomberg) */
    [data-testid="stMetricValue"] {
        color: #FFB900 !important; 
        font-family: 'Courier New', monospace;
    }
    
    /* Etiquetas de métricas en gris claro */
    [data-testid="stMetricLabel"] {
        color: #AAAAAA !important;
    }

    /* Caja de Recomendación: Más sobria */
    .stAlert {
        background-color: #1E2633; /* Azul muy oscuro tipo institucional */
        color: #FFFFFF;
        border: 1px solid #2E5CB8;
    }

    /* Tablas: Encabezados destacados y filas limpias */
    .stTable {
        color: #E0E0E0;
        background-color: #121212;
    }
    thead tr th {
        background-color: #252525 !important;
        color: #FFB900 !important;
    }
    </style>
    """, unsafe_allow_html=True)
import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="AgroCFO-GPT Rosario", layout="wide")

# --- BARRA LATERAL (Sidebar) ---
st.sidebar.image("https://www.bcr.com.ar/sites/default/files/logo-bcr.png", width=150)
st.sidebar.title("Panel de Control")
st.sidebar.write("Bienvenido, Operador Pérez")

# Subida de archivos (Lo que Claude va a leer)
uploaded_file = st.sidebar.file_uploader("Subir PDF (USDA, BCR, Normativas)", type=["pdf", "csv", "xlsx"])

if uploaded_file:
    st.sidebar.success("Archivo cargado correctamente")

# --- CUERPO PRINCIPAL ---
st.title("📊 Terminal de Inteligencia Agroeconómica")
st.markdown("### Nodo Rosario | Análisis Integral de Granos")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Soja Rosario (Pizarra)", value="$265.000", delta="+1.2%")
    st.write("**Sentimiento USDA:** Bearish 🔴")

with col2:
    st.metric(label="Dólar MEP", value="$1.150", delta="-0.5%")
    st.write("**Basis Rosario/Chicago:** -12.50 USD/Tn")

with col3:
    st.metric(label="Tasa Badlar (BCRA)", value="42%", delta="0%")
    st.write("**Riesgo Logístico:** Medio (Demoras en Timbúes)")

st.divider()

# Sección de Recomendación de la IA
st.subheader("🤖 Recomendación Estratégica (AgroCFO-GPT)")
st.info("""
**Análisis de Claude:** Dada la subida de Chicago y el Basis actual en Rosario, 
se sugiere no entregar mercadería física hoy. Conviene capturar valor mediante 
un Forward a mayo y cubrir el riesgo con la compra de un Put en Matba Rofex.
""")

# Tabla de Canje (Simulada)
st.subheader("🚜 Optimizador de Canje Técnico")
data = {
    'Insumo': ['Fertilizante nitrogenado', 'Semilla Soja Enlist', 'Glifosato'],
    'Precio Contado (USD)': [550, 45, 8],
    'Ratio Canje Sugerido': [2.1, 0.17, 0.03],
    'Ahorro Impositivo Est.': ["10.5%", "10.5%", "21%"]
}
df = pd.DataFrame(data)
st.table(df)
