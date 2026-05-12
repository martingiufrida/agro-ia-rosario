import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Terminal Agro | Dashboard", layout="wide")

# 2. FUNCIÓN DE GRÁFICOS (Usando símbolos libres de licencia)
def crear_chart_agro(ticker_tv):
    return f"""
    <div style="height:350px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true,
          "symbol": "{ticker_tv}",
          "interval": "D",
          "timezone": "America/Argentina/Buenos_Aires",
          "theme": "light",
          "style": "1",
          "locale": "es",
          "toolbar_bg": "#f1f3f6",
          "enable_publishing": false,
          "hide_top_toolbar": true,
          "hide_legend": true,
          "save_image": false,
          "container_id": "tv_chart_{ticker_tv.split(':')[-1]}"
        }});
        </script>
        <div id="tv_chart_{ticker_tv.split(':')[-1]}" style="height:350px;"></div>
    </div>
    """

# 3. BARRA LATERAL
st.sidebar.title("Terminal Agro")
archivo = st.sidebar.file_uploader("Cargar Informes", type=["pdf", "csv", "xlsx"])

# 4. HEADER Y MÉTRICAS
st.title("Terminal de Inteligencia Agroeconómica")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("SOJA ROSARIO", "$265.000", "+1.2%")
with m2:
    st.metric("MAÍZ ROSARIO", "$168.000", "-0.8%")
with m3:
    st.metric("DÓLAR MEP", "$1.150", "-0.5%")
with m4:
    st.metric("BASIS (USD)", "-12.50", "BCR/CME")

st.divider()

# 5. MONITOREO TRIPLE (Símbolos de libre acceso)
st.subheader("Monitor de Mercados Globales (Referencia Chicago)")
col_soja, col_maiz, col_trigo = st.columns(3)

with col_soja:
    st.write("### SOJA (ZS)")
    # Usamos CAPITALCOM:SOYBEAN para evitar el bloqueo de licencia
    components.html(crear_chart_agro("CAPITALCOM:SOYBEAN"), height=360)

with col_maiz:
    st.write("### MAÍZ (ZC)")
    # Usamos CAPITALCOM:CORN
    components.html(crear_chart_agro("CAPITALCOM:CORN"), height=360)

with col_trigo:
    st.write("### TRIGO (ZW)")
    # Usamos CAPITALCOM:WHEAT
    components.html(crear_chart_agro("CAPITALCOM:WHEAT"), height=360)

st.divider()

# 6. PANEL DE ANÁLISIS E INSUMOS
col_ia, col_table = st.columns([1, 1.5])

with col_ia:
    st.subheader("Recomendación Estratégica")
    st.info("""
    **Análisis:** Se observa soporte técnico en Chicago. Se recomienda 
    reforzar coberturas sobre Maíz y esperar mejora de Basis en Soja.
    """)

with col_table:
    st.subheader("Ratio de Canje")
    data = {
        'Insumo': ['Urea', 'Semilla Soja', 'Fosfato'],
        'Precio USD': [540, 48, 720],
        'Ratio Soja': [2.04, 0.18, 2.71],
        'Detalle': ["IVA 10.5%", "Financiado", "SISA Cat 1"]
    }
    st.table(pd.DataFrame(data))
