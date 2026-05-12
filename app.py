import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import plotly.graph_objects as go

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Agro-Terminal Pro", layout="wide", initial_sidebar_state="expanded")

# 2. CSS PARA IMITAR EL ESTILO KOYFIN
st.markdown("""
    <style>
    /* Fondo general oscuro */
    .stApp { background-color: #12141A; color: #E0E0E0; font-family: 'Inter', sans-serif; }
    
    /* Fondo de la barra lateral tipo Koyfin */
    [data-testid="stSidebar"] {
        background-color: #1A1C24;
        border-right: 1px solid #2A2D3A;
    }
    
    /* Títulos de las categorías del menú (ej: DASHBOARDS, PORTFOLIO TOOLS) */
    .menu-category {
        color: #8A909D;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1px;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        padding-left: 0.5rem;
    }

    /* Convertir botones nativos en enlaces de navegación */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        border: none !important;
        background-color: transparent !important;
        color: #C5C9D1 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 0.4rem 0.5rem !important;
        font-size: 0.95rem !important;
        border-radius: 4px !important;
        box-shadow: none !important;
    }
    
    /* Efecto al pasar el mouse (Hover) */
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2A2D3A !important;
        color: #FFFFFF !important;
    }
    
    /* Quitar el borde rojo molesto al hacer clic */
    [data-testid="stSidebar"] .stButton > button:focus {
        background-color: #2A2D3A !important;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. LÓGICA DE MEMORIA PARA LA NAVEGACIÓN (Session State)
if 'menu_activo' not in st.session_state:
    st.session_state.menu_activo = "Mercados Hoy"

def set_menu(nombre_menu):
    st.session_state.menu_activo = nombre_menu

# Función para ponerle una flecha al menú seleccionado
def formato_btn(nombre, icono):
    if st.session_state.menu_activo == nombre:
        return f"▶ {icono} {nombre}" # Menú activo
    return f"  {icono} {nombre}"     # Menú inactivo

# 4. CONSTRUCCIÓN DEL MENÚ LATERAL (SIDEBAR)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Koyfin_Logo.png/1200px-Koyfin_Logo.png", width=120) # Logo de ejemplo
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Categoría 1: DASHBOARDS
st.sidebar.markdown("<div class='menu-category'>DASHBOARDS</div>", unsafe_allow_html=True)
if st.sidebar.button(formato_btn("Mercados Hoy", "🌎"), use_container_width=True): set_menu("Mercados Hoy")
if st.sidebar.button(formato_btn("Screener Local", "📊"), use_container_width=True): set_menu("Screener Local")

# Categoría 2: FUNDAMENTAL & RESEARCH
st.sidebar.markdown("<div class='menu-category'>ANÁLISIS FUNDAMENTAL</div>", unsafe_allow_html=True)
if st.sidebar.button(formato_btn("S&D Global (USDA)", "🌾"), use_container_width=True): set_menu("S&D Global (USDA)")
if st.sidebar.button(formato_btn("Noticias & Drivers", "📰"), use_container_width=True): set_menu("Noticias & Drivers")

# Categoría 3: PORTFOLIO TOOLS (Agro)
st.sidebar.markdown("<div class='menu-category'>HERRAMIENTAS OPERATIVAS</div>", unsafe_allow_html=True)
if st.sidebar.button(formato_btn("Derivados & Opciones", "📈"), use_container_width=True): set_menu("Derivados & Opciones")
if st.sidebar.button(formato_btn("Calculadora de Canje", "🚜"), use_container_width=True): set_menu("Calculadora de Canje")


# 5. FUNCIONES DE APOYO (TradingView)
def crear_chart_agro(ticker_tv):
    return f"""
    <div style="height:350px;">
        <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
        <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true, "symbol": "{ticker_tv}", "interval": "D",
          "theme": "dark", "style": "1", "locale": "es", "toolbar_bg": "#12141A",
          "hide_top_toolbar": true, "hide_legend": true,
          "container_id": "tv_{ticker_tv.split(':')[-1]}"
        }});
        </script>
        <div id="tv_{ticker_tv.split(':')[-1]}" style="height:350px;"></div>
    </div>
    """

# ==========================================
# 6. PANTALLAS (El contenido cambia según el menú)
# ==========================================

# --- PANTALLA 1: MERCADOS HOY ---
if st.session_state.menu_activo == "Mercados Hoy":
    st.title("🌎 Mercados Hoy")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("SOJA ROSARIO", "$265.000", "+1.2%")
    m2.metric("MAÍZ ROSARIO", "$168.000", "-0.8%")
    m3.metric("DÓLAR MEP", "$1.150", "-0.5%")
    m4.metric("BASIS (USD)", "-12.50", "BCR/CME")

    st.divider()
    col_s, col_m, col_t = st.columns(3)
    with col_s:
        st.markdown("##### SOJA (ZS)")
        components.html(crear_chart_agro("CAPITALCOM:SOYBEAN"), height=360)
    with col_m:
        st.markdown("##### MAÍZ (ZC)")
        components.html(crear_chart_agro("CAPITALCOM:CORN"), height=360)
    with col_t:
        st.markdown("##### TRIGO (ZW)")
        components.html(crear_chart_agro("CAPITALCOM:WHEAT"), height=360)

# --- PANTALLA 2: S&D GLOBAL ---
elif st.session_state.menu_activo == "S&D Global (USDA)":
    st.title("🌾 Balance Mundial (S&D)")
    st.write("Evolución del balance de oferta y demanda proyectado.")
    
    campanas = ['22/23', '23/24', '24/25 (P)']
    produccion = [382, 395, 398] 
    consumo = [365, 384, 390]
    stock_use = 26.4 

    c1, c2 = st.columns([2, 1])
    with c1:
        fig_bar = go.Figure(data=[
            go.Bar(name='Producción', x=campanas, y=produccion, marker_color='#2E5CB8'),
            go.Bar(name='Consumo', x=campanas, y=consumo, marker_color='#8A909D')
        ])
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#C5C9D1"))
        st.plotly_chart(fig_bar, use_container_width=True)
    with c2:
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = stock_use, title = {'text': "Stock-to-Use %", 'font': {'color': '#C5C9D1'}},
            gauge = {'axis': {'range': [None, 40]}, 'bar': {'color': "#FFB900"}}))
        fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#C5C9D1"))
        st.plotly_chart(fig_gauge, use_container_width=True)

# --- PANTALLA 3: SCREENER LOCAL ---
elif st.session_state.menu_activo == "Screener Local":
    st.title("📊 Screener Pizarra y Forward")
    st.write("Comparativa de terminales Up-River vs Sur.")
    st.table(pd.DataFrame({
        'Terminal': ['San Lorenzo', 'Timbúes', 'Bahía Blanca', 'Quequén'],
        'Soja Disponible': [265000, 265000, 268000, 266000],
        'Maíz Disponible': [168000, 167500, 172000, 171000],
        'Cupos': ['Normal', 'Demoras', 'Normal', 'Normal']
    }))

# --- PANTALLAS RESTANTES (En construcción) ---
else:
    st.title(f"🛠️ {st.session_state.menu_activo}")
    st.write("Este módulo está en construcción. Aquí integraremos las respuestas del agente Claude para análisis de opciones y calculadoras de margen.")
