"""
AgroTerminal Institucional v1.1
Modo: SOLO LECTURA. Prohibida toda funcion de envio de ordenes.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import yfinance as yf
from datetime import datetime, timedelta
import warnings
import time

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------
# MATRIZ MAESTRA
# ---------------------------------------------------------------
MATRIZ_MAESTRA = {
    "cme": {
        "soja":  {"ticker": "ZS=F", "factor_ton": 36.7437, "nombre": "Soja Chicago"},
        "maiz":  {"ticker": "ZC=F", "factor_ton": 39.3683, "nombre": "Maiz Chicago"},
        "trigo": {"ticker": "ZW=F", "factor_ton": 36.7437, "nombre": "Trigo Chicago"},
    },
    "argentina_datos": {
        "oficial": "https://api.argentinadatos.com/v1/cotizaciones/dolares/oficial",
        "ccl":     "https://api.argentinadatos.com/v1/cotizaciones/dolares/contadoconliqui",
        "mep":     "https://api.argentinadatos.com/v1/cotizaciones/dolares/mep",
        "blend_w":   0.80,
        "blend_ccl": 0.20,
    },
    "nasa_power": {
        "base_url":   "https://power.larc.nasa.gov/api/temporal/daily/point",
        "community":  "AG",
        "parameters": "PRECTOTCORR,T2M_MAX,T2M_MIN,ALLSKY_SFC_SW_DWN",
        "format":     "JSON",
        "zona_nucleo": {"lat": -32.9468, "lon": -60.6393, "nombre": "Rosario"},
        "pergamino":   {"lat": -33.8882, "lon": -60.5696, "nombre": "Pergamino"},
    },
    "alpha_vantage": {
        "base_url": "https://www.alphavantage.co/query",
        "function": "NEWS_SENTIMENT",
        "tickers":  "CRYSTAL:SOYBEAN,CRYSTAL:CORN,CRYSTAL:WHEAT",
        "topics":   "economy_macro,finance,manufacturing",
    },
    "usda_fas": {
        "base_url": "https://api.fas.usda.gov",
        "commodities": {
            "soja":  {"code": "2222000", "nombre": "Soybeans"},
            "maiz":  {"code": "0440000", "nombre": "Corn"},
            "trigo": {"code": "0410000", "nombre": "Wheat"},
        },
        "attribute_ids": {
            "ending_stocks":      176,
            "total_distribution": 125,
            "production":          28,
            "imports":             57,
        },
    },
    "rofex": {
        "tickers": {
            "soja":  ["SOJ/ENE26", "SOJ/MAY26", "SOJ/NOV25"],
            "maiz":  ["MAI/ENE26", "MAI/MAR26", "MAI/ABR26"],
            "trigo": ["TRI/ENE26", "TRI/MAR26", "TRI/ABR26"],
        },
    },
    "gastos_exportacion": {
        "fobbing":        12.0,
        "flete_interno":   8.0,
        "portuarios":      5.0,
        "paritaria":       2.5,
        "total":          27.5,
    },
    "dex_vigente": {
        "soja":    0.26,
        "maiz":    0.09,
        "trigo":   0.09,
        "girasol": 0.07,
    },
    "maas_model": {
        "kc_soja":               1.2,
        "etp_referencia_mm_dia": 5.5,
        "capacidad_campo_mm":  200.0,
        "punto_marchitez_mm":   80.0,
        "lluvia_critica_p30":  350.0,
    },
}

# ---------------------------------------------------------------
# CONFIGURACION DE PAGINA
# ---------------------------------------------------------------
st.set_page_config(
    page_title="AgroTerminal | Institucional",
    page_icon="T",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap');
html, body, [class*="css"] {
  font-family: 'JetBrains Mono', 'Consolas', monospace !important;
  background-color: #0a0a0f !important;
  color: #c8ccd4 !important;
}
.main { background-color: #0a0a0f !important; }
.block-container { padding: 0.5rem 1rem 1rem 1rem !important; max-width: 100% !important; }
[data-testid="stSidebar"] {
  background-color: #0d0d17 !important;
  border-right: 1px solid #1e2030 !important;
}
[data-testid="stSidebar"] * { color: #8b9bb4 !important; font-size: 0.72rem !important; }
.ticker-tape {
  background: #0d0d17; border-bottom: 2px solid #ff6600;
  padding: 6px 16px; font-size: 0.78rem;
  font-family: 'JetBrains Mono', monospace;
  display: flex; gap: 28px; overflow-x: auto;
  white-space: nowrap; margin-bottom: 8px; align-items: center;
}
.t-label { color: #6b7280; font-size: 0.65rem; margin-right: 4px; }
.t-val   { color: #e2e8f0; font-weight: 700; }
.t-up    { color: #00e676 !important; font-size: 0.68rem; }
.t-dn    { color: #ff3d00 !important; font-size: 0.68rem; }
.t-gold  { color: #ffd600 !important; font-weight: 700; }
.ph {
  background: linear-gradient(90deg, #0d1117 0%, #131825 100%);
  border-left: 3px solid #ff6600; padding: 4px 10px;
  font-size: 0.68rem; color: #ff6600; letter-spacing: 0.12em;
  text-transform: uppercase; font-weight: 700; margin-bottom: 6px;
}
.ps {
  border-left: 3px solid #1565c0; padding: 3px 8px;
  font-size: 0.63rem; color: #5c7cfa; letter-spacing: 0.1em;
  text-transform: uppercase; margin-bottom: 4px; margin-top: 6px;
}
.kcard {
  background: #0d1117; border: 1px solid #1e2030;
  border-radius: 2px; padding: 8px 12px; margin-bottom: 5px;
}
.kl  { font-size: 0.60rem; color: #6b7280; letter-spacing: 0.08em; text-transform: uppercase; }
.kv  { font-size: 1.0rem; font-weight: 700; color: #e2e8f0; line-height: 1.3; }
.kd-up { font-size: 0.63rem; color: #00e676; }
.kd-dn { font-size: 0.63rem; color: #ff3d00; }
.a-red { background:#1a0505; border:1px solid #ff3d00; border-radius:2px; padding:6px 10px; font-size:0.68rem; color:#ff6b6b; margin:4px 0; }
.a-grn { background:#051a0a; border:1px solid #00e676; border-radius:2px; padding:6px 10px; font-size:0.68rem; color:#69f0ae; margin:4px 0; }
.a-org { background:#1a0f05; border:1px solid #ff9100; border-radius:2px; padding:6px 10px; font-size:0.68rem; color:#ffcc02; margin:4px 0; }
.ni   { background:#0d1117; border-left:2px solid #1565c0; padding:6px 10px; margin:3px 0; font-size:0.67rem; line-height:1.5; }
.ni-b { border-left-color: #00e676 !important; }
.ni-s { border-left-color: #ff3d00 !important; }
.ni-n { border-left-color: #ff9100 !important; }
.sc-b { color:#00e676; font-weight:700; }
.sc-s { color:#ff3d00; font-weight:700; }
.stDataFrame table { font-size:0.69rem !important; font-family:'JetBrains Mono',monospace !important; }
.stDataFrame th { background-color:#131825 !important; color:#ff6600 !important; }
.stDataFrame td { border-bottom:1px solid #1e2030 !important; color:#c8ccd4 !important; }
.stButton > button {
  background:#0d1117 !important; color:#ff6600 !important;
  border:1px solid #ff6600 !important;
  font-family:'JetBrains Mono',monospace !important;
  font-size:0.7rem !important; border-radius:2px !important; padding:4px 12px !important;
}
.stButton > button:hover { background:#ff6600 !important; color:#000 !important; }
hr { border-color:#1e2030 !important; margin:4px 0 !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------
# CREDENCIALES
# ---------------------------------------------------------------
def get_secret(key, default=""):
    try:
        return st.secrets[key]
    except Exception:
        return default


ROFEX_USER    = get_secret("ROFEX_USER")
ROFEX_PASS    = get_secret("ROFEX_PASS")
ROFEX_ACCOUNT = get_secret("ROFEX_ACCOUNT")
USDA_KEY      = get_secret("USDA_KEY",         "YYqF02MPMumT8ioD1sss6FQ9bYvJNROxlr0QyAXi")
AV_KEY        = get_secret("ALPHA_VANTAGE_KEY", "Q6M04D8LVQCHKIJ4")


# ---------------------------------------------------------------
# INGESTA DE DATOS
# ---------------------------------------------------------------

@st.cache_data(ttl=60)
def fetch_cme_prices():
    result = {}
    for commodity, cfg in MATRIZ_MAESTRA["cme"].items():
        try:
            hist = yf.Ticker(cfg["ticker"]).history(period="5d", interval="1d")
            if hist.empty:
                result[commodity] = {"precio_usd_ton": None, "variacion_pct": None}
                continue
            last       = float(hist["Close"].iloc[-1])
            prev       = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else last
            price      = (last / 100.0) * cfg["factor_ton"]
            prev_price = (prev / 100.0) * cfg["factor_ton"]
            var        = ((price - prev_price) / prev_price * 100) if prev_price else 0.0
            result[commodity] = {
                "precio_usd_ton": round(price, 2),
                "variacion_pct":  round(var, 2),
                "raw_cents":      round(last, 2),
                "nombre":         cfg["nombre"],
            }
        except Exception as e:
            result[commodity] = {"precio_usd_ton": None, "variacion_pct": None, "error": str(e)}
    return result


@st.cache_data(ttl=120)
def fetch_dolares_blend():
    cfg = MATRIZ_MAESTRA["argentina_datos"]
    out = {"mayorista": None, "ccl": None, "mep": None, "blend": None}

    def _get(url):
        try:
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, list) and data:
                    return float(data[-1].get("venta", data[-1].get("valor", 0)))
                if isinstance(data, dict):
                    return float(data.get("venta", data.get("valor", 0)))
        except Exception:
            pass
        return None

    out["mayorista"] = _get(cfg["oficial"])
    out["ccl"]       = _get(cfg["ccl"])
    out["mep"]       = _get(cfg["mep"])
    if out["mayorista"] and out["ccl"]:
        out["blend"] = round(
            cfg["blend_w"] * out["mayorista"] + cfg["blend_ccl"] * out["ccl"], 2
        )
    return out


@st.cache_data(ttl=300)
def fetch_rofex_market_data():
    result = {}
    try:
        import pyRofex

        if not ROFEX_USER or not ROFEX_PASS:
            raise ValueError("Credenciales ROFEX no configuradas en st.secrets")

        pyRofex.initialize(
            user=ROFEX_USER,
            password=ROFEX_PASS,
            account=ROFEX_ACCOUNT,
            environment=pyRofex.Environment.REMARKET,
        )

        entries = [
            pyRofex.MarketDataEntry.BIDS,
            pyRofex.MarketDataEntry.OFFERS,
            pyRofex.MarketDataEntry.LAST,
            pyRofex.MarketDataEntry.OPEN_INTEREST,
            pyRofex.MarketDataEntry.VOLUME,
            pyRofex.MarketDataEntry.SETTLEMENT_PRICE,
        ]

        for commodity, tickers in MATRIZ_MAESTRA["rofex"]["tickers"].items():
            posiciones = []
            for ticker in tickers:
                try:
                    md  = pyRofex.get_market_data(ticker=ticker, entries=entries)
                    mkt = md.get("marketData", {}) if md and md.get("status") == "OK" else {}
                    posiciones.append({
                        "ticker":      ticker,
                        "bid":         mkt.get("BI", [{}])[0].get("price") if mkt.get("BI") else None,
                        "ask":         mkt.get("OF", [{}])[0].get("price") if mkt.get("OF") else None,
                        "ultimo":      mkt.get("LA", {}).get("price"),
                        "volumen":     mkt.get("TV"),
                        "int_abierto": mkt.get("OI"),
                        "ajuste":      mkt.get("SP"),
                    })
                except Exception:
                    posiciones.append({"ticker": ticker, "bid": None, "ask": None, "ultimo": None})
            result[commodity] = posiciones

    except ImportError:
        result["_error"] = "pyRofex no instalado"
    except Exception as e:
        result["_error"] = str(e)

    return result


@st.cache_data(ttl=3600)
def fetch_nasa_power(lat, lon, dias=30):
    cfg      = MATRIZ_MAESTRA["nasa_power"]
    end_dt   = datetime.now() - timedelta(days=1)
    start_dt = end_dt - timedelta(days=dias)
    params   = {
        "parameters": cfg["parameters"],
        "community":  cfg["community"],
        "longitude":  lon,
        "latitude":   lat,
        "start":      start_dt.strftime("%Y%m%d"),
        "end":        end_dt.strftime("%Y%m%d"),
        "format":     cfg["format"],
    }
    try:
        r = requests.get(cfg["base_url"], params=params, timeout=20)
        if r.status_code == 200:
            props = r.json().get("properties", {}).get("parameter", {})
            dates = list(props.get("PRECTOTCORR", {}).keys())
            df = pd.DataFrame({
                "fecha":  pd.to_datetime(dates, format="%Y%m%d"),
                "lluvia": list(props.get("PRECTOTCORR", {}).values()),
                "tmax":   list(props.get("T2M_MAX", {}).values()),
                "tmin":   list(props.get("T2M_MIN", {}).values()),
                "rad":    list(props.get("ALLSKY_SFC_SW_DWN", {}).values()),
            })
            return df.replace(-999.0, np.nan).sort_values("fecha").reset_index(drop=True)
    except Exception:
        pass
    return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_usda_psd(commodity_code, market_year):
    url     = f"https://api.fas.usda.gov/api/psd/commodity/{commodity_code}/world/year/{market_year}"
    headers = {"X-Api-Key": USDA_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                return pd.DataFrame(data)
    except Exception:
        pass
    return pd.DataFrame()


@st.cache_data(ttl=600)
def fetch_alpha_vantage_news():
    cfg    = MATRIZ_MAESTRA["alpha_vantage"]
    params = {
        "function": cfg["function"],
        "tickers":  cfg["tickers"],
        "topics":   cfg["topics"],
        "apikey":   AV_KEY,
        "limit":    20,
        "sort":     "RELEVANCE",
    }
    try:
        r = requests.get(cfg["base_url"], params=params, timeout=15)
        if r.status_code == 200:
            return r.json().get("feed", [])[:12]
    except Exception:
        pass
    return []


@st.cache_data(ttl=86400)
def load_historical_series():
    try:
        df_raw = pd.read_excel(
            "/mnt/project/Serie_historia_SOJAMAIZGIRASOLTRIGO.xlsx",
            sheet_name="Serie historia SOJA-MAIZ-GIRASO",
            header=0,
        )
        dfs = []
        for g in [(1, 2, 3, 4), (6, 7, 8, 9), (11, 12, 13, 14), (16, 17, 18, 19)]:
            sub = df_raw.iloc[1:, list(g)].copy()
            sub.columns = ["Fecha", "Mercado", "Producto", "Precio"]
            sub = sub.dropna(subset=["Fecha", "Precio"])
            sub["Fecha"]  = pd.to_datetime(sub["Fecha"], errors="coerce")
            sub["Precio"] = pd.to_numeric(sub["Precio"], errors="coerce")
            dfs.append(sub.dropna())
        return pd.concat(dfs, ignore_index=True).sort_values("Fecha")
    except Exception:
        return pd.DataFrame(columns=["Fecha", "Mercado", "Producto", "Precio"])


# ---------------------------------------------------------------
# MODELOS CUANTITATIVOS
# ---------------------------------------------------------------

def calcular_fas_teorico(fob, commodity, dex_override=None):
    gastos = MATRIZ_MAESTRA["gastos_exportacion"]["total"]
    dex    = dex_override if dex_override is not None else MATRIZ_MAESTRA["dex_vigente"].get(commodity, 0.09)
    return {
        "fob":         fob,
        "dex_pct":     dex * 100,
        "retencion":   round(fob * dex, 2),
        "gastos":      gastos,
        "fas_teorico": round(fob * (1 - dex) - gastos, 2),
    }


def calcular_blend_ars(usd_ton, dolares):
    blend = dolares.get("blend")
    return round(usd_ton * blend, 2) if blend and blend > 0 else None


def modelo_maas(df_clima):
    cfg = MATRIZ_MAESTRA["maas_model"]
    if df_clima.empty:
        return {"error": "Sin datos climaticos"}
    df           = df_clima.copy()
    df["etc"]    = cfg["kc_soja"] * cfg["etp_referencia_mm_dia"]
    df["deficit"] = (df["etc"] - df["lluvia"]).clip(lower=0)
    lluvia_acum  = float(df["lluvia"].sum())
    deficit_acum = float(df["deficit"].sum())
    balance      = lluvia_acum - float(df["etc"].sum())
    reserva      = float(np.clip(
        cfg["capacidad_campo_mm"] / 2 + balance,
        cfg["punto_marchitez_mm"],
        cfg["capacidad_campo_mm"],
    ))
    if lluvia_acum < cfg["lluvia_critica_p30"] * 0.70:
        nivel = "CRITICO"
    elif lluvia_acum < cfg["lluvia_critica_p30"]:
        nivel = "MODERADO"
    else:
        nivel = "NORMAL"
    return {
        "lluvia_acum_mm":  round(lluvia_acum, 1),
        "deficit_acum_mm": round(deficit_acum, 1),
        "balance_neto_mm": round(balance, 1),
        "reserva_au_mm":   round(reserva, 1),
        "nivel_riesgo":    nivel,
        "umbral_p30_mm":   cfg["lluvia_critica_p30"],
        "df":              df,
    }


def calcular_stu(df_psd):
    if df_psd.empty or "attributeId" not in df_psd.columns:
        return {}
    cfg = MATRIZ_MAESTRA["usda_fas"]["attribute_ids"]
    try:
        ending  = df_psd[df_psd["attributeId"] == cfg["ending_stocks"]]["value"].sum()
        distrib = df_psd[df_psd["attributeId"] == cfg["total_distribution"]]["value"].sum()
        prod    = df_psd[df_psd["attributeId"] == cfg["production"]]["value"].sum()
        stu     = (ending / distrib * 100) if distrib > 0 else None
        return {
            "ending_stocks_mmt": round(ending  / 1000, 1),
            "total_distrib_mmt": round(distrib / 1000, 1),
            "produccion_mmt":    round(prod    / 1000, 1),
            "stock_to_use_pct":  round(stu, 1) if stu else None,
        }
    except Exception:
        return {}


# ---------------------------------------------------------------
# TEMA PLOTLY
# ---------------------------------------------------------------
LAYOUT_BASE = dict(
    plot_bgcolor  = "#0a0a0f",
    paper_bgcolor = "#0a0a0f",
    font          = dict(family="JetBrains Mono, Consolas, monospace", color="#c8ccd4", size=10),
    xaxis=dict(gridcolor="#1e2030", linecolor="#2d3147", zeroline=False),
    yaxis=dict(gridcolor="#1e2030", linecolor="#2d3147", zeroline=False),
    legend=dict(bgcolor="#0d1117", bordercolor="#1e2030", borderwidth=1, font=dict(size=9)),
    margin=dict(l=40, r=20, t=30, b=30),
    colorway=["#ff6600", "#00e676", "#5c7cfa", "#ffd600", "#e040fb", "#00b0ff"],
)

COLORS = {"Soja": "#ff6600", "Maiz": "#ffd600", "Trigo": "#5c7cfa", "Girasol": "#00e676"}


# ---------------------------------------------------------------
# GRAFICOS
# ---------------------------------------------------------------

def chart_historico(df_hist, commodities):
    fig = go.Figure()
    for c in commodities:
        sub = df_hist[df_hist["Producto"].str.lower() == c.lower()].copy()
        if sub.empty:
            continue
        color = COLORS.get(c, "#c8ccd4")
        fig.add_trace(go.Scatter(
            x=sub["Fecha"], y=sub["Precio"], name=c,
            line=dict(color=color, width=1.5),
            hovertemplate="<b>%{fullData.name}</b><br>%{x|%d/%m/%Y}<br>ARS/Ton: %{y:,.0f}<extra></extra>",
        ))
        if len(sub) >= 50:
            sub = sub.copy()
            sub["ma50"] = sub["Precio"].rolling(50).mean()
            fig.add_trace(go.Scatter(
                x=sub["Fecha"], y=sub["ma50"],
                name=c + " MA50",
                line=dict(color=color, width=0.8, dash="dot"),
                opacity=0.5, showlegend=False,
            ))
    fig.update_layout(**LAYOUT_BASE)
    fig.update_layout(
        height=300, hovermode="x unified",
        yaxis=dict(tickformat=",.0f"),
        title=dict(
            text="SERIE HISTORICA PRECIOS ROSARIO (ARS/Ton)",
            font=dict(size=10, color="#ff6600"), x=0,
        ),
    )
    return fig


def chart_arbitraje(df_hist, cme_data, dolares):
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=("PRECIO ROSARIO vs PARIDAD CHICAGO (USD/Ton)", "BASIS (Rosario - Chicago)"),
        row_heights=[0.65, 0.35],
    )
    soja    = df_hist[df_hist["Producto"] == "Soja"].tail(260).copy()
    blend   = dolares.get("blend")
    chicago = cme_data.get("soja", {}).get("precio_usd_ton")

    if not soja.empty and blend and blend > 0:
        soja["rosario_usd"] = soja["Precio"] / blend
        fig.add_trace(go.Scatter(
            x=soja["Fecha"], y=soja["rosario_usd"],
            name="Rosario Spot USD",
            line=dict(color="#ff6600", width=1.5),
        ), row=1, col=1)
        if chicago:
            fig.add_hline(
                y=chicago,
                line=dict(color="#5c7cfa", width=1, dash="dash"),
                annotation_text=f"CME {chicago:.1f}",
                row=1, col=1,
            )
            soja["basis"] = soja["rosario_usd"] - chicago
            fig.add_trace(go.Bar(
                x=soja["Fecha"], y=soja["basis"],
                name="Basis USD/Ton",
                marker_color=np.where(soja["basis"] >= 0, "#00e676", "#ff3d00"),
            ), row=2, col=1)
            fig.add_hline(y=0, line=dict(color="#6b7280", width=0.5), row=2, col=1)

    fig.update_layout(**LAYOUT_BASE)
    fig.update_layout(height=320, showlegend=True)
    return fig


def chart_clima(maas_result):
    if "error" in maas_result or "df" not in maas_result:
        return go.Figure()
    df  = maas_result["df"]
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=("PRECIPITACIONES vs ETC (mm/dia)", "TEMPERATURA (C)"),
        row_heights=[0.55, 0.45],
    )
    fig.add_trace(go.Bar(
        x=df["fecha"], y=df["lluvia"],
        name="Lluvia mm", marker_color="#00b0ff", opacity=0.8,
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df["fecha"], y=df["etc"],
        name="ETc Soja", line=dict(color="#ff6600", width=1.5, dash="dot"),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df["fecha"], y=df["tmax"],
        name="T Max", line=dict(color="#ff3d00", width=1),
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=df["fecha"], y=df["tmin"],
        name="T Min", line=dict(color="#00e676", width=1),
        fill="tonexty", fillcolor="rgba(0,230,118,0.05)",
    ), row=2, col=1)
    fig.update_layout(**LAYOUT_BASE)
    fig.update_layout(height=300)
    return fig


def chart_estacionalidad(df_hist):
    fig   = go.Figure()
    meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    for c in ["Soja", "Maiz", "Trigo"]:
        sub = df_hist[df_hist["Producto"] == c].copy()
        if sub.empty:
            continue
        sub["mes"] = pd.to_datetime(sub["Fecha"]).dt.month
        avg    = sub.groupby("mes")["Precio"].mean().reindex(range(1, 13))
        std    = avg.std()
        normed = ((avg - avg.mean()) / std * 100).values if std > 0 else avg.values
        fig.add_trace(go.Scatter(
            x=meses, y=normed, name=c,
            line=dict(color=COLORS.get(c, "#c8ccd4"), width=1.5),
            mode="lines+markers", marker=dict(size=5),
        ))
    fig.add_hline(y=0, line=dict(color="#6b7280", width=0.8, dash="dot"))
    fig.update_layout(**LAYOUT_BASE)
    fig.update_layout(
        height=230,
        title=dict(
            text="ESTACIONALIDAD - DESVIO NORMALIZADO PRECIO PROMEDIO MENSUAL",
            font=dict(size=9, color="#ff6600"), x=0,
        ),
        yaxis_title="Score Z",
    )
    return fig


def chart_stu_gauge(stu_value, commodity):
    color = "#ff3d00" if stu_value < 12 else "#ff9100" if stu_value < 18 else "#00e676"
    fig   = go.Figure(go.Indicator(
        mode="gauge+number",
        value=stu_value,
        number=dict(suffix="%", font=dict(color=color, size=22)),
        title=dict(text=f"STOCK/USE {commodity.upper()}", font=dict(color="#8b9bb4", size=10)),
        gauge=dict(
            axis=dict(range=[0, 35], tickcolor="#6b7280", tickfont=dict(size=8)),
            bar=dict(color=color, thickness=0.25),
            bgcolor="#0d1117",
            bordercolor="#1e2030",
            steps=[
                dict(range=[0,  12], color="#2a0505"),
                dict(range=[12, 20], color="#2a1a05"),
                dict(range=[20, 35], color="#051a0a"),
            ],
            threshold=dict(
                line=dict(color="#ffd600", width=2),
                thickness=0.75, value=15,
            ),
        ),
    ))
    fig.update_layout(**LAYOUT_BASE)
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=10))
    return fig


# ---------------------------------------------------------------
# COMPONENTES UI
# ---------------------------------------------------------------

def render_ticker(cme_data, dolares):
    items = []
    blend = dolares.get("blend")
    if blend:
        items.append(
            f'<span class="t-label">BLEND</span><span class="t-gold">{blend:.2f}</span>'
            f'&nbsp;<span class="t-label">OFIC</span><span class="t-val">{dolares.get("mayorista", 0):.2f}</span>'
            f'&nbsp;<span class="t-label">CCL</span><span class="t-val">{dolares.get("ccl", 0):.2f}</span>'
            f'&nbsp;<span class="t-label">MEP</span><span class="t-val">{dolares.get("mep", 0):.2f}</span>'
        )
    for commodity, d in cme_data.items():
        precio = d.get("precio_usd_ton")
        var    = d.get("variacion_pct") or 0.0
        if not precio:
            continue
        cls    = "t-up" if var >= 0 else "t-dn"
        arrow  = "+" if var >= 0 else ""
        nombre = d.get("nombre", commodity.upper())
        items.append(
            f'<span class="t-label">{nombre}</span>'
            f'<span class="t-val">{precio:.1f}</span>'
            f'&nbsp;<span class="{cls}">{arrow}{var:.2f}%</span>'
        )
    ts = datetime.now().strftime("%d/%m/%Y %H:%M")
    items.append(f'<span class="t-label">{ts} ART</span>')
    st.markdown(
        '<div class="ticker-tape">' + "&nbsp;&nbsp;|&nbsp;&nbsp;".join(items) + "</div>",
        unsafe_allow_html=True,
    )


def kpi(label, value, delta=None, up=None):
    delta_html = ""
    if delta is not None:
        cls        = "kd-up" if up else "kd-dn"
        delta_html = f'<div class="{cls}">{delta}</div>'
    st.markdown(
        f'<div class="kcard"><div class="kl">{label}</div>'
        f'<div class="kv">{value}</div>{delta_html}</div>',
        unsafe_allow_html=True,
    )


def render_rofex(rofex_data):
    if "_error" in rofex_data:
        st.markdown(
            f'<div class="a-org">ROFEX: {rofex_data["_error"]} - configurar credenciales en st.secrets</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="ps">DATOS DEMO - REMARKET DESCONECTADO</div>', unsafe_allow_html=True)
        demo = pd.DataFrame({
            "Ticker": ["SOJ/ENE26", "SOJ/MAY26", "SOJ/NOV25", "MAI/ENE26", "MAI/MAR26", "TRI/ENE26"],
            "Bid":    [275.0, 268.5, 285.0, 178.0, 182.5, 195.0],
            "Ask":    [276.5, 270.0, 286.5, 179.5, 183.5, 196.5],
            "Ultimo": [275.8, 269.0, 285.5, 178.5, 183.0, 195.5],
            "Spread": [1.5,   1.5,   1.5,   1.5,   1.0,   1.5],
            "IA":     [12500, 8700,  5400,  22000, 15000, 9800],
        })
        st.dataframe(demo, use_container_width=True, hide_index=True, height=230)
        return
    rows = []
    for commodity, posiciones in rofex_data.items():
        for pos in posiciones:
            bid = pos.get("bid")
            ask = pos.get("ask")
            rows.append({
                "Ticker": pos.get("ticker"),
                "Bid":    bid,
                "Ask":    ask,
                "Ultimo": pos.get("ultimo"),
                "Spread": round(ask - bid, 2) if bid and ask else None,
                "IA":     pos.get("int_abierto"),
                "Ajuste": pos.get("ajuste"),
            })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=250)


def render_arbitraje(cme_data, dolares, cfg_dex):
    rows = []
    for commodity in ["soja", "maiz", "trigo"]:
        precio_chicago = cme_data.get(commodity, {}).get("precio_usd_ton")
        if not precio_chicago:
            continue
        fob = precio_chicago * 1.004
        fas = calcular_fas_teorico(fob, commodity, cfg_dex.get(commodity))
        liq = calcular_blend_ars(fas["fas_teorico"], dolares)
        rows.append({
            "Commodity":   commodity.upper(),
            "FOB Ref":     f"USD {fob:.1f}",
            "DEX":         f"{fas['dex_pct']:.0f}%",
            "Retencion":   f"USD {fas['retencion']:.1f}",
            "Gastos":      f"USD {fas['gastos']:.1f}",
            "FAS Teorico": f"USD {fas['fas_teorico']:.1f}",
            "Liq ARS/Ton": f"{liq:,.0f}" if liq else "N/D",
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, height=175)


def render_noticias(feed):
    if not feed:
        st.markdown(
            '<div class="a-org">Alpha Vantage: sin datos - verificar cuota de API.</div>',
            unsafe_allow_html=True,
        )
        return
    for item in feed[:6]:
        title  = item.get("title", "")[:115]
        source = item.get("source", "")
        ts_raw = item.get("time_published", "")[:8]
        score  = float(item.get("overall_sentiment_score", 0))
        url    = item.get("url", "#")
        if score > 0.15:
            ni_cls, sc_cls, tag = "ni ni-b", "sc-b", "BULL"
        elif score < -0.15:
            ni_cls, sc_cls, tag = "ni ni-s", "sc-s", "BEAR"
        else:
            ni_cls, sc_cls, tag = "ni ni-n", "", "NEUT"
        ts_fmt = f"{ts_raw[:4]}-{ts_raw[4:6]}-{ts_raw[6:]}" if len(ts_raw) >= 8 else ts_raw
        st.markdown(
            f'<div class="{ni_cls}">'
            f'<span class="{sc_cls}">[{tag} {score:+.3f}]</span> '
            f'<a href="{url}" target="_blank" style="color:#c8ccd4;text-decoration:none"><b>{title}</b></a>'
            f'<br><span style="color:#6b7280;font-size:0.6rem">{source} | {ts_fmt}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_fundamental(stu_data, commodity):
    if not stu_data:
        st.markdown(
            '<div class="a-org">USDA FAS: sin datos de balance disponibles.</div>',
            unsafe_allow_html=True,
        )
        return
    c1, c2 = st.columns(2)
    with c1:
        kpi("PRODUCCION MUNDIAL (MMT)", f"{stu_data.get('produccion_mmt', 0):.1f}")
        kpi("ENDING STOCKS (MMT)",      f"{stu_data.get('ending_stocks_mmt', 0):.1f}")
        kpi("TOTAL DISTRIB (MMT)",      f"{stu_data.get('total_distrib_mmt', 0):.1f}")
    with c2:
        stu = stu_data.get("stock_to_use_pct")
        if stu:
            st.plotly_chart(
                chart_stu_gauge(stu, commodity),
                use_container_width=True,
                config={"displayModeBar": False},
            )


# ---------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown('<div class="ph">CONFIGURACION TERMINAL</div>', unsafe_allow_html=True)

        st.markdown('<div class="ps">COORDENADAS CLIMATICAS</div>', unsafe_allow_html=True)
        zona = st.selectbox("Zona", ["Rosario", "Pergamino", "Manual"])
        if zona == "Rosario":
            lat, lon = -32.9468, -60.6393
        elif zona == "Pergamino":
            lat, lon = -33.8882, -60.5696
        else:
            lat = st.number_input("Latitud",  value=-32.95, format="%.4f")
            lon = st.number_input("Longitud", value=-60.64, format="%.4f")

        dias_clima = st.slider("Horizonte clima (dias)", 15, 60, 30, 5)

        st.markdown('<div class="ps">PARAMETROS DEX</div>', unsafe_allow_html=True)
        dex_soja  = st.slider("DEX Soja (%)",  0, 40, 26, 1) / 100
        dex_maiz  = st.slider("DEX Maiz (%)",  0, 20,  9, 1) / 100
        dex_trigo = st.slider("DEX Trigo (%)", 0, 20,  9, 1) / 100

        st.markdown('<div class="ps">VISUALIZACION HISTORICA</div>', unsafe_allow_html=True)
        commodities_sel = st.multiselect(
            "Commodities",
            ["Soja", "Maiz", "Trigo", "Girasol"],
            default=["Soja", "Maiz", "Trigo"],
        )
        anios_hist = st.slider("Anios de historia", 1, 24, 5)

        st.markdown('<div class="ps">USDA FUNDAMENTAL</div>', unsafe_allow_html=True)
        usda_commodity = st.selectbox("Commodity USDA", ["soja", "maiz", "trigo"])
        market_year    = st.selectbox("Campaign Year",  [2025, 2024, 2023, 2022])

        st.markdown("---")
        auto_refresh = st.checkbox("Auto-refresh 60s", value=False)
        if auto_refresh:
            time.sleep(60)
            st.rerun()

        st.markdown(
            '<div style="font-size:0.55rem;color:#3d4455;margin-top:8px">'
            'MODO: SOLO LECTURA | v1.1</div>',
            unsafe_allow_html=True,
        )

    return {
        "lat":            lat,
        "lon":            lon,
        "dias_clima":     dias_clima,
        "dex":            {"soja": dex_soja, "maiz": dex_maiz, "trigo": dex_trigo},
        "commodities_sel": commodities_sel,
        "anios_hist":     anios_hist,
        "usda_commodity": usda_commodity,
        "market_year":    market_year,
    }


# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------
def main():
    cfg = render_sidebar()

    with st.spinner(""):
        cme_data   = fetch_cme_prices()
        dolares    = fetch_dolares_blend()
        rofex_data = fetch_rofex_market_data()

    render_ticker(cme_data, dolares)

    st.markdown(
        '<div style="font-size:0.62rem;color:#6b7280;letter-spacing:0.14em;margin-bottom:4px">'
        'AGROTERMINAL INSTITUCIONAL // MERCADO DE GRANOS // ZONA NUCLEO ARGENTINA</div>',
        unsafe_allow_html=True,
    )

    # FILA 1 - CME + ROFEX
    col1, col2 = st.columns([1.4, 1.6])

    with col1:
        st.markdown('<div class="ph">PRECIOS CME CHICAGO (USD/Ton)</div>', unsafe_allow_html=True)
        c_a, c_b, c_c = st.columns(3)
        for col, key in zip([c_a, c_b, c_c], ["soja", "maiz", "trigo"]):
            with col:
                d      = cme_data.get(key, {})
                precio = d.get("precio_usd_ton")
                var    = d.get("variacion_pct") or 0.0
                kpi(
                    key.upper(),
                    f"{precio:.1f}" if precio else "N/D",
                    f"{'+'if var>=0 else ''}{var:.2f}%" if precio else None,
                    var >= 0,
                )

        st.markdown('<div class="ps">TIPO DE CAMBIO</div>', unsafe_allow_html=True)
        c_d, c_e, c_f = st.columns(3)
        with c_d:
            kpi("MAYORISTA",   f"{dolares.get('mayorista', 0):.2f}" if dolares.get("mayorista") else "N/D")
        with c_e:
            kpi("CCL",         f"{dolares.get('ccl', 0):.2f}"       if dolares.get("ccl")       else "N/D")
        with c_f:
            kpi("BLEND 80/20", f"{dolares.get('blend', 0):.2f}"     if dolares.get("blend")     else "N/D", up=True)

    with col2:
        st.markdown('<div class="ph">MATBA-ROFEX TERMINO ROSARIO (USD/Ton)</div>', unsafe_allow_html=True)
        render_rofex(rofex_data)

    st.markdown("---")

    # FILA 2 - HISTORICO + ARBITRAJE
    col3, col4 = st.columns([1.6, 1.4])

    with col3:
        st.markdown('<div class="ph">SERIE HISTORICA - MERCADO FISICO ROSARIO</div>', unsafe_allow_html=True)
        df_hist = load_historical_series()
        if not df_hist.empty:
            cutoff = datetime.now() - timedelta(days=365 * cfg["anios_hist"])
            df_f   = df_hist[df_hist["Fecha"] >= cutoff]
            st.plotly_chart(
                chart_historico(df_f, cfg["commodities_sel"]),
                use_container_width=True, config={"displayModeBar": False},
            )
        else:
            st.warning("Serie historica no disponible")

        st.markdown('<div class="ps">ESTACIONALIDAD</div>', unsafe_allow_html=True)
        if not df_hist.empty:
            st.plotly_chart(
                chart_estacionalidad(df_hist),
                use_container_width=True, config={"displayModeBar": False},
            )

    with col4:
        st.markdown('<div class="ph">ARBITRAJE - BASIS Y PARIDAD EXPORTACION</div>', unsafe_allow_html=True)
        render_arbitraje(cme_data, dolares, cfg["dex"])

        st.markdown('<div class="ps">EVOLUCION BASIS SOJA (USD/Ton)</div>', unsafe_allow_html=True)
        if not df_hist.empty:
            st.plotly_chart(
                chart_arbitraje(df_hist, cme_data, dolares),
                use_container_width=True, config={"displayModeBar": False},
            )

    st.markdown("---")

    # FILA 3 - CLIMA + NOTICIAS + FUNDAMENTAL
    col5, col6, col7 = st.columns([1.2, 1.4, 1.4])

    with col5:
        st.markdown('<div class="ph">MONITOR CLIMATICO - BALANCE HIDRICO MAAS 1982</div>',
                    unsafe_allow_html=True)
        df_clima = fetch_nasa_power(cfg["lat"], cfg["lon"], cfg["dias_clima"])
        maas     = modelo_maas(df_clima)

        if "nivel_riesgo" in maas:
            css = {"CRITICO": "a-red", "MODERADO": "a-org", "NORMAL": "a-grn"}.get(
                maas["nivel_riesgo"], "a-org")
            st.markdown(
                f'<div class="{css}">RIESGO RINDE: <strong>{maas["nivel_riesgo"]}</strong>'
                f' | Lluvia 30d: {maas["lluvia_acum_mm"]} mm'
                f' (umbral P30: {maas["umbral_p30_mm"]} mm)</div>',
                unsafe_allow_html=True,
            )
            h1, h2 = st.columns(2)
            with h1:
                kpi("LLUVIA ACUM (mm)",  f"{maas['lluvia_acum_mm']:.1f}")
                kpi("DEFICIT ACUM (mm)", f"{maas['deficit_acum_mm']:.1f}", up=False)
            with h2:
                kpi("RESERVA AU (mm)",   f"{maas['reserva_au_mm']:.1f}")
                kpi("BALANCE NETO (mm)", f"{maas['balance_neto_mm']:.1f}",
                    up=maas["balance_neto_mm"] >= 0)
            st.plotly_chart(
                chart_clima(maas),
                use_container_width=True, config={"displayModeBar": False},
            )
        else:
            st.warning("NASA POWER: sin datos para las coordenadas seleccionadas")

    with col6:
        st.markdown('<div class="ph">RADAR DE NOTICIAS - SENTIMENT ANALYSIS</div>',
                    unsafe_allow_html=True)
        render_noticias(fetch_alpha_vantage_news())

    with col7:
        st.markdown('<div class="ph">ANALISIS FUNDAMENTAL - USDA PSD BALANCE MUNDIAL</div>',
                    unsafe_allow_html=True)
        usda_cfg = MATRIZ_MAESTRA["usda_fas"]["commodities"][cfg["usda_commodity"]]
        df_psd   = fetch_usda_psd(usda_cfg["code"], cfg["market_year"])
        stu_data = calcular_stu(df_psd)
        render_fundamental(stu_data, cfg["usda_commodity"])

        if not df_psd.empty and "attributeId" in df_psd.columns:
            with st.expander("RAW PSD DATA", expanded=False):
                st.dataframe(
                    df_psd[["attributeId", "unitId", "value", "marketYear"]].head(25),
                    use_container_width=True, height=180,
                )

    st.markdown("---")
    st.markdown(
        '<div style="font-size:0.57rem;color:#3d4455;text-align:center;padding:4px">'
        'AgroTerminal Institucional v1.1 | MODO SOLO LECTURA | '
        'Fuentes: CME/yfinance - Matba-Rofex/pyRofex - USDA FAS PSD - NASA POWER - Alpha Vantage - ArgentinaDatos | '
        'Datos con fines informativos, no constituyen recomendacion de inversion.'
        '</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
