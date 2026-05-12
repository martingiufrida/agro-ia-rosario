
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

# --- SECCIÓN DE GRÁFICOS (ESTILO TERMINAL) ---
st.divider()
st.subheader("📈 Monitoreo de Futuros (CME Group)")

# ESTA ES LA LÍNEA QUE SEGURO TE FALTA:
tab1, tab2, tab3 = st.tabs(["SOJA (ZS)", "MAÍZ (ZC)", "TRIGO (ZW)"])

# Luego vienen los bloques que usan esas pestañas
with tab1:
    components.html(crear_chart("ZS"), height=410)

with tab2:
    components.html(crear_chart("ZC"), height=410)

with tab3:
    components.html(crear_chart("ZW"), height=410)
