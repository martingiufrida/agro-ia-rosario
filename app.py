# AgroTerminal Institucional v1.0

Terminal de información de mercado agroeconómico institucional.
Arquitectura de alta densidad, estilo Bloomberg Terminal.

## Stack Tecnológico

# Frontend: Streamlit + Plotly (modo oscuro, JetBrains Mono)
# Datos Internacionales: yfinance (CME - ZS=F, ZC=F, ZW=F)
# Macro Local: ArgentinaDatos API (Mayorista A3500, CCL, MEP)
# Termino Local: pyRofex (Matba-Rofex REMARKET)
# Fundamental: USDA FAS PSD API (balance mundial oferta/demanda)
# Clima: NASA POWER (PRECTOTCORR, T2M, RAD - modelo Maas 1982)
# Sentimiento: Alpha Vantage NEWS_SENTIMENT

## Instalación

```bash
pip install -r requirements.txt
mkdir -p .streamlit
cp secrets.toml.template .streamlit/secrets.toml
# Editar .streamlit/secrets.toml con credenciales reales
streamlit run app.py
```

## Estructura de Módulos

```
app.py
├── MATRIZ_MAESTRA          # Diccionario central de configuración APIs
├── fetch_cme_prices()      # CME via yfinance (cents/bu -> USD/Ton)
├── fetch_dolares_blend()   # ArgentinaDatos (Blend 80/20)
├── fetch_rofex_market_data()  # pyRofex REMARKET (SOLO LECTURA)
├── fetch_nasa_power()      # NASA POWER balance hídrico
├── fetch_usda_psd()        # USDA FAS PSD balance mundial
├── fetch_alpha_vantage_news() # Sentiment granos
├── load_historical_series()   # XLSX serie histórica BCR
├── calcular_fas_teorico()  # FAS = FOB*(1-DEX) - gastos
├── calcular_basis()        # Basis = Rosario - Chicago
├── modelo_maas_balance_hidrico() # Modelo Maas (1982)
└── calcular_stock_to_use() # STU = Ending Stocks / Total Distrib
```

## Conversiones CME

| Commodity | Factor bu/MT | Fórmula |
|-----------|-------------|---------|
| Soja      | 36.7437     | cents/bu / 100 * 36.7437 |
| Maiz      | 39.3683     | cents/bu / 100 * 39.3683 |
| Trigo     | 36.7437     | cents/bu / 100 * 36.7437 |

## Módulo Climático (Maas 1982)

Implementa balance hídrico simplificado:
- ETc = Kc_soja (1.2) * ETP_referencia (5.5 mm/dia)
- Déficit = max(0, ETc - Lluvia_dia)
- Reserva_AU = f(Capacidad_Campo=200mm, PMP=80mm)
- Alerta CRITICO: lluvia_acum < 70% del percentil histórico P30 (350mm)
- Alerta MODERADO: lluvia_acum < P30

## Parámetros DEX Vigentes (configurables en sidebar)

- Soja: 26%
- Maiz: 9%
- Trigo: 9%
- Girasol: 7%

## Gastos de Exportación Up-River (USD/Ton)

| Concepto       | USD/Ton |
|---------------|---------|
| Fobbing        | 12.0   |
| Flete interno  | 8.0    |
| Portuarios     | 5.0    |
| Paritaria      | 2.5    |
| **Total**      | **27.5** |

## USDA PSD Commodity Codes

- Soja: 2222000
- Maiz: 0440000
- Trigo: 0410000

## Modo SOLO LECTURA

La terminal no expone ni invoca `send_order`, `place_order` ni ninguna función
de envío de órdenes de pyRofex. Acceso exclusivamente a Market Data.

## TTL de Cache por Fuente

| Fuente           | TTL    |
|-----------------|--------|
| CME (yfinance)  | 60s    |
| ArgentinaDatos  | 120s   |
| Matba-Rofex     | 300s   |
| Alpha Vantage   | 600s   |
| USDA PSD        | 3600s  |
| NASA POWER      | 3600s  |
| Serie histórica | 86400s |
