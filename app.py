import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="AgroCFO-GPT | Terminal Bloomberg", layout="wide")

# 2. ESTILO BLOOMBERG MODERNO (CSS)
st.markdown("""
    <style>
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 { color: #FFFFFF !important; }
    [data-testid="stSidebar"] {
        background-color: #1A1A1A;
        border-right: 1px solid #333333;
    }
    [data-testid="stMetricValue"] {
        color: #FFB900 !important; 
        font-family: 'Courier New', monospace;
    }
    [data-testid="stMetricLabel"] { color: #AAAAAA !important; }
    .stAlert {
        background-color: #1E2633;
        color: #FFFFFF;
        border: 1px solid #2E5CB8;
    }
    /* Estilo para las Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #1A1A1A;
        padding: 10px;
        border-radius: 5px 5px 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        color: #AAAAAA !important;
    }
    .stTabs [aria-selected="true"] {
        color: #FFB900 !important;
        border-bottom: 2px solid #FFB900 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIÓN PARA GENERAR GRÁFICOS (TRADINGVIEW)
def crear_chart(ticker):
    return f"""
    <div style="height:400px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true,
          "symbol": "CBOT:{ticker}1!",
          "interval": "D",
          "timezone": "America/Argentina/Buenos_Aires",
          "theme": "dark",
          "style": "1",
          "locale": "es",
          "toolbar_bg": "#f1f3f6",
          "enable_publishing": false,
          "hide_top_toolbar": true,
          "save_image": false,
          "container_id": "tv_chart_{ticker}"
        }});
        </script>
        <div id="tv_chart_{ticker}" style="height:400px;"></div>
    </div>
    """

# 4. BARRA LATERAL (SIDEBAR)
st.sidebar.title("Panel de Control")
st.sidebar.write("AgroCFO-GPT v1.0")
uploaded_file = st.sidebar.file_uploader("Cargar Informes (PDF/Excel)", type=["pdf", "csv", "xlsx"])

if uploaded_file:
    st.sidebar.success("Archivo procesado")

# 5. ENCABEZADO Y MÉTRICAS
st.title("📊 Terminal de Inteligencia Agroeconómica")
st.markdown("### Nodo Rosario | Análisis de Mercados")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Soja Rosario (Pizarra)", value="$265.000", delta="+1.2%")
    st.write("**Sentimiento:** Neutral 🟡")
with col2:
    st.metric(label="Dólar MEP", value="$1.150", delta="-0.5%")
    st.write("**Basis:** -12.50 USD/Tn")
with col3:
    st.metric(label="Tasa Badlar", value="42%", delta="0%")
    st.write("**Logística:** Demoras en Timbúes")

st.divider()

# 6. SECCIÓN DE RECOMENDACIÓN IA
st.subheader("🤖 Recomendación Estratégica")
st.info("""
**Análisis Estratégico:** Se observa una resistencia técnica en los futuros de soja mayo. 
Dada la brecha cambiaria actual, se recomienda cobertura mediante PUTs y esperar 
mejoras en el Basis local antes de fijar mercadería física.
""")

# 7. MONITOREO DE FUTUROS (GRÁFICOS)
st.divider()
st.subheader("📈 Monitoreo de Futuros (CME Group)")
tab1, tab2, tab3 = st.tabs(["SOJA (ZS)", "MAÍZ (ZC)", "TRIGO (ZW)"])

with tab1:
    components.html(crear_chart("ZS"), height=410)
with tab2:
    components.html(crear_chart("ZC"), height=410)
with tab3:
    components.html(crear_chart("ZW"), height=410)

# 8. TABLA DE RATIOS
st.divider()
st.subheader("🚜 Optimizador de Canje e Insumos")
data = {
    'Insumo': ['Fertilizante', 'Semilla Enlist', 'Glifosato'],
    'Precio (USD)': [550, 45, 8],
    'Ratio Canje': [2.1, 0.17, 0.03],
    'Ahorro IVA': ["10.5%", "10.5%", "21%"]
}
st.table(pd.DataFrame(data))
