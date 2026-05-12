import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import plotly.graph_objects as go

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Terminal Agro | Operativa", layout="wide")

# 2. FUNCIÓN GRÁFICOS TRADINGVIEW (Símbolos Libres)
def crear_chart_agro(ticker_tv):
    return f"""
    <div style="height:350px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true, "symbol": "{ticker_tv}", "interval": "D",
          "timezone": "America/Argentina/Buenos_Aires", "theme": "light",
          "style": "1", "locale": "es", "toolbar_bg": "#f1f3f6",
          "enable_publishing": false, "hide_top_toolbar": true,
          "hide_legend": true, "save_image": false,
          "container_id": "tv_chart_{ticker_tv.split(':')[-1]}"
        }});
        </script>
        <div id="tv_chart_{ticker_tv.split(':')[-1]}" style="height:350px;"></div>
    </div>
    """

# 3. SIDEBAR
st.sidebar.title("Terminal Agro")
archivo = st.sidebar.file_uploader("Cargar Informes", type=["pdf", "csv", "xlsx"])

# 4. HEADER Y MÉTRICAS
st.title("Terminal de Inteligencia Agroeconómica")
m1, m2, m3, m4 = st.columns(4)
with m1: st.metric("SOJA ROSARIO", "$265.000", "+1.2%")
with m2: st.metric("MAÍZ ROSARIO", "$168.000", "-0.8%")
with m3: st.metric("DÓLAR MEP", "$1.150", "-0.5%")
with m4: st.metric("BASIS (USD)", "-12.50", "BCR/CME")

st.divider()

# 5. MONITOREO TRIPLE
st.subheader("Monitor de Futuros (Referencia Chicago)")
col_soja, col_maiz, col_trigo = st.columns(3)
with col_soja:
    st.write("### SOJA (ZS)")
    components.html(crear_chart_agro("CAPITALCOM:SOYBEAN"), height=360)
with col_maiz:
    st.write("### MAÍZ (ZC)")
    components.html(crear_chart_agro("CAPITALCOM:CORN"), height=360)
with col_trigo:
    st.write("### TRIGO (ZW)")
    components.html(crear_chart_agro("CAPITALCOM:WHEAT"), height=360)

st.divider()

# 6. ANÁLISIS FUNDAMENTAL (PLOTLY)
st.subheader("🌎 Análisis Fundamental: Balance Global (USDA)")
campanas = ['22/23', '23/24', '24/25 (P)']
produccion = [382, 395, 398] 
consumo = [365, 384, 390]
stock_use_ratio = 26.4 

col_chart, col_gauge = st.columns([2, 1])
with col_chart:
    fig_bar = go.Figure(data=[
        go.Bar(name='Producción', x=campanas, y=produccion, marker_color='#2E5CB8'),
        go.Bar(name='Consumo', x=campanas, y=consumo, marker_color='#AAAAAA')
    ])
    fig_bar.update_layout(barmode='group', height=350, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_bar, use_container_width=True)

with col_gauge:
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = stock_use_ratio,
        title = {'text': "Stock-to-Use %"},
        gauge = {'axis': {'range': [None, 40]}, 'bar': {'color': "#FFB900"},
                 'steps': [{'range': [0, 20], 'color': "#FF4B4B"}, {'range': [20, 30], 'color': "#FFFF33"}, {'range': [30, 40], 'color': "#00CC66"}]}))
    fig_gauge.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

st.divider()

# 7. TABLA DE RATIOS
st.subheader("🚜 Optimizador de Canje")
data = {'Insumo': ['Urea', 'Semilla Soja', 'Fosfato'], 'Precio USD': [540, 48, 720], 'Ratio Soja': [2.04, 0.18, 2.71]}
st.table(pd.DataFrame(data))
