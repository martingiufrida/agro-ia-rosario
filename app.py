import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import plotly.graph_objects as go

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Agro-Terminal Pro", layout="wide")

# 2. BARRA LATERAL (MENÚ EXTENSO)
st.sidebar.title("🛠️ Menú de Terminal")
menu = st.sidebar.selectbox(
    "Seleccionar Módulo:",
    [
        "Dashboard General", 
        "Stock/Consumo Global", 
        "Derivados Financieros", 
        "Screener Mercado Local",
        "Macro & Bonos",
        "Calculadora de Canje"
    ]
)

st.sidebar.divider()
st.sidebar.info(f"Módulo activo: **{menu}**")

# 3. FUNCIONES DE APOYO (GRÁFICOS)
def crear_chart_agro(ticker_tv):
    return f"""
    <div style="height:400px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true, "symbol": "{ticker_tv}", "interval": "D",
          "theme": "light", "style": "1", "locale": "es", "hide_top_toolbar": true,
          "container_id": "tv_{ticker_tv.split(':')[-1]}"
        }});
        </script>
        <div id="tv_{ticker_tv.split(':')[-1]}" style="height:400px;"></div>
    </div>
    """

# --- LÓGICA DE NAVEGACIÓN ---

if menu == "Dashboard General":
    st.title("🛡️ Terminal de Inteligencia Agroeconómica")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("SOJA ROSARIO", "$265.000", "+1.2%")
    m2.metric("MAÍZ ROSARIO", "$168.000", "-0.8%")
    m3.metric("DÓLAR MEP", "$1.150", "-0.5%")
    m4.metric("BASIS (USD)", "-12.50", "BCR/CME")
    
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("### SOJA (ZS)")
        components.html(crear_chart_agro("CAPITALCOM:SOYBEAN"), height=410)
    with col2:
        st.write("### MAÍZ (ZC)")
        components.html(crear_chart_agro("CAPITALCOM:CORN"), height=410)
    with col3:
        st.write("### TRIGO (ZW)")
        components.html(crear_chart_agro("CAPITALCOM:WHEAT"), height=410)

elif menu == "Stock/Consumo Global":
    st.title("🌎 Análisis Fundamental (S&D)")
    st.markdown("### Balances Globales del USDA")
    
    # Aquí va la lógica de Plotly que armamos antes
    campanas = ['22/23', '23/24', '24/25 (P)']
    produccion = [382, 395, 398] 
    consumo = [365, 384, 390]
    stock_use_ratio = 26.4 

    c1, c2 = st.columns([2, 1])
    with c1:
        fig = go.Figure(data=[
            go.Bar(name='Producción', x=campanas, y=produccion, marker_color='#2E5CB8'),
            go.Bar(name='Consumo', x=campanas, y=consumo, marker_color='#AAAAAA')
        ])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig_g = go.Figure(go.Indicator(
            mode = "gauge+number", value = stock_use_ratio,
            title = {'text': "Stock-to-Use %"},
            gauge = {'axis': {'range': [None, 40]}, 'bar': {'color': "#FFB900"}}))
        st.plotly_chart(fig_g, use_container_width=True)

elif menu == "Derivados Financieros":
    st.title("📈 Monitor de Derivados")
    st.write("Espacio reservado para análisis de Volatilidad Implícita y Griegas de Opciones (Matba Rofex).")
    # Podés agregar un gráfico de TradingView de la acción de GGAL o Futuros de Soja
    components.html(crear_chart_agro("BCBA:GGAL"), height=500)

elif menu == "Screener Mercado Local":
    st.title("📊 Screener de Precios Rosario")
    st.write("Comparativa de precios Pizarra vs. Mercado a Término.")
    df_local = pd.DataFrame({
        'Puerto': ['Rosario', 'Quequén', 'Bahía Blanca'],
        'Soja Spot': [265000, 262000, 267000],
        'Maíz Spot': [168000, 165000, 170000],
        'Basis vs Chicago': [-12.5, -15.2, -10.8]
    })
    st.table(df_local)

elif menu == "Calculadora de Canje":
    st.title("🚜 Optimizador de Canje")
    st.write("Calculá el beneficio financiero de canjear granos por insumos.")
    precio_insumo = st.number_input("Precio Insumo (USD/Tn)", value=550)
    precio_grano = st.number_input("Precio Grano Rosario (USD/Tn)", value=280)
    
    ratio = precio_insumo / precio_grano
    st.metric("Ratio de Canje", f"{ratio:.2f} Tn de grano por Tn de insumo")
    st.info("Recordá que el canje evita el impuesto al cheque y permite deducir IVA.")

else:
    st.title("Monitor Macro & Bonos")
    st.write("Seguimiento de la curva de bonos soberanos y tasas del BCRA.")
