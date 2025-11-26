import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# -------------------------
# This application is the property of Stephen Cohen / Papushkado ; cannot be used for sale. 
# If you want to create something, we can surely build it together. 
# -------------------------


# -------------------------
# TICKER—NAME MAPPING
# -------------------------
TICKERS_DICT = {
    "AC.PA": "Accor", "AI.PA": "Air Liquide", "AIR.PA": "Airbus", "AKE.PA": "Arkema", "ALO.PA": "Alstom",
    "ALD.PA": "ALD", "ATO.PA": "Atos", "MT.AS": "ArcelorMittal", "AUB.PA": "Aubay", "AUD.PA": "Aubert & Duval",
    "A2E.PA": "2CRSI", "BEN.PA": "Beneteau", "BNP.PA": "BNP Paribas", "EN.PA": "Bouygues",
    "CAP.PA": "Capgemini", "CA.PA": "Carrefour", "COFA.PA": "Coface", "CRL.PA": "CRH (Euronext Paris)",
    "CS.PA": "AXA", "DBV.PA": "DBV Technologies", "DSY.PA": "Dassault Systèmes", "EDEN.PA": "Edenred",
    "EI.PA": "EssilorLuxottica", "EL.PA": "Legrand", "ENGI.PA": "Engie", "ERF.PA": "Eramet",
    "ETL.PA": "Eutelsat", "EUX.PA": "Euronext", "FGR.PA": "Covivio", "FNAC.PA": "Fnac Darty", "FR.PA": "Valeo",
    "FRE.PA": "Faurecia", "GENP.PA": "Genfit", "GET.PA": "Getlink", "GLPG.AS": "Galapagos",
    "GLP.PA": "Groupe Legrand Publicitaire", "GTT.PA": "Gaztransport & Technigaz", "HEL.PA": "Hermès International",
    "HO.PA": "Thales", "ILIAD.PA": "Iliad", "IMB.PA": "Imerys", "INGA.AS": "ING", "IPS.PA": "Ipsen",
    "ITP.PA": "Interparfums", "KER.PA": "Kering", "KORI.PA": "Korian", "LEGR.PA": "Legrand",
    "LHA.DE": "Lufthansa", "LLD.PA": "Linedata Services", "LOIM.PA": "Laurent-Perrier", "LR.PA": "Legrand",
    "LVMH.PA": "LVMH", "MC.PA": "LVMH (alias)", "MDT.PA": "Medtronic", "MDG.PA": "M6-Metropole Television",
    "MIC.PA": "Michelin", "MMP.PA": "Mercialys", "MN.PA": "Mersen", "MRN.PA": "Maurette", "NEOEN.PA": "Neoen",
    "NEX.PA": "Nexans", "NXI.PA": "Nexity", "OR.PA": "L'Oréal", "ORA.PA": "Orange", "OTIS.PA": "Otis Worldwide",
    "PARP.PA": "Paref", "POM.PA": "Poujoulat", "PUB.PA": "Publicis", "QFB.PA": "Quartix Holdings",
    "RCO.PA": "Renault", "RMS.PA": "Hermès", "RI.PA": "Pernod Ricard", "RNO.PA": "Renault", "SAF.PA": "Safran",
    "SAM.PA": "Somfy", "SAN.PA": "Sanofi", "SAP.PA": "Sartorius Stedim Biotech", "SGO.PA": "Saint-Gobain",
    "SLB.PA": "Schlumberger", "SOP.PA": "Sopra Steria Group", "SRP.PA": "Showroomprivé", "STLA.PA": "Stellantis",
    "SU.PA": "Schneider Electric", "SW.PA": "Sodexo", "SY.PA": "Synergie", "TEC.PA": "Technip Energies",
    "TTF.PA": "Teleperformance", "TTE.PA": "TotalEnergies", "UBI.PA": "Ubisoft Entertainment",
    "UL.PA": "Unibail-Rodamco-Westfield", "VIE.PA": "Veolia Environnement", "VIV.PA": "Vivendi",
    "VK.PA": "Vallourec", "WLN.PA": "Worldline"
}
TICKER_CHOICES = [f"{name} ({ticker})" for ticker, name in TICKERS_DICT.items()]

# ------------------------------------------
# YIELDS & CRYPTO UTILITIES
# ------------------------------------------
def get_rate_yield(ticker):
    try:
        dta = yf.Ticker(ticker).history(period="1d")
        if len(dta) > 0:
            last = dta["Close"].iloc[-1]
            if ticker == "^TNX":
                return f"{round(last, 2)}"
            else:
                return f"{round(last * 100, 2)}"
    except Exception:
        pass
    return "Data unavailable"

def get_asset_price(ticker):
    try:
        dta = yf.Ticker(ticker).history(period="1d")
        if len(dta) > 0:
            return f"{round(dta['Close'].iloc[-1], 2):,}"
    except Exception:
        pass
    return "Data unavailable"

# ------------------------------------------
# FUNCTION TO GET TICKER DATA
# ------------------------------------------
@st.cache_data(show_spinner=False)
def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    def gv(key): return info[key] if key in info else np.nan
    try:
        data = {
            'Name': gv('shortName'),
            'Ticker': ticker,
            'Price': gv('currentPrice'),
            'P/E': gv('trailingPE'),
            'P/B': gv('priceToBook'),
            'EPS': gv('trailingEps'),
            'Debt/Equity': gv('debtToEquity'),
            'Dividend Yield (%)': gv('dividendYield') * 100 if gv('dividendYield') else np.nan,
            'Market Cap (Bn €)': gv('marketCap')/1e9 if gv('marketCap') else np.nan,
            'Net Profit >0': gv('profitMargins') > 0 if 'profitMargins' in info else np.nan,
            'Dividend/year': gv('dividendRate'),
        }
    except Exception:
        data = {k: np.nan for k in [
            'Name', 'Ticker', 'Price', 'P/E', 'P/B', 'EPS',
            'Debt/Equity', 'Dividend Yield (%)', 'Market Cap (Bn €)',
            'Net Profit >0', 'Dividend/year'
        ]}
        data['Name'] = TICKERS_DICT.get(ticker, ticker)
        data['Ticker'] = ticker
    return data

# ------------------------------------------
# APP UI
# ------------------------------------------
st.set_page_config(page_title="Graham SBF120 Stock Picker", layout="wide")
st.title("🔎 Graham Stock Picker - SBF120")
st.caption("Analyze the SBF120 according to Benjamin Graham's value principles. Enhanced version: real-time bond yields and crypto prices.")

# -- HEADER WITH LIVE METRICS --
cols = st.columns(5)
cols[0].metric("US 10Y Yield", f"{get_rate_yield('^TNX')}%")
cols[1].metric("FR 10Y Yield", f"{get_rate_yield('^FR10Y')}%")
cols[2].metric("DE 10Y Yield", f"{get_rate_yield('^DE10Y')}%")
cols[3].metric("BTC/USD", f"${get_asset_price('BTC-USD')}")
cols[4].metric("ETH/USD", f"${get_asset_price('ETH-USD')}")

st.markdown("""\
_This tool screens SBF120 stocks based on the legendary **Benjamin Graham** value criteria. Use the sliders below to explore the market!_
""")

# --------- GRAHAM CRITERIA & HELP ----------
with st.expander("Selection criteria (hover for help)", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        per_max = st.slider(
            "Maximum P/E",
            5.0, 30.0, 15.0,
            help="Price/Earnings Ratio. Graham recommended a P/E below 15."
        )
        pb_max = st.slider(
            "Maximum Price/Book",
            0.5, 5.0, 1.5,
            help="Price to Book Value ratio. Graham ideally recommended a maximum of 1.5."
        )
    with col2:
        dette_max = st.slider(
            "Max Debt/Equity (%)",
            0, 300, 100,
            help="Net debt to equity (in %). Graham recommended less than 100%."
        )
        cap_min = st.slider(
            "Minimum Market Cap (Bn €)",
            0, 20, 2,
            help="Minimum market capitalization requirement to limit business risk. Graham suggested a significant size (> 2 Bn € equivalent in today's value)."
        )
    with col3:
        div_min = st.slider(
            "Minimum Dividend Yield (%)",
            0.0, 10.0, 2.0,
            help="Dividend yield above the market average. Graham recommended at least 2 to 3%."
        )

# --------- SELECTION & ANALYSIS ---------
selected_names = st.multiselect(
    "Select the stocks to analyze",
    options=TICKER_CHOICES,
    default=TICKER_CHOICES[:12],
    help="You will see the stock name and its ticker."
)
selected_tickers = [c.split("(")[-1].replace(")", "").strip() for c in selected_names]

if st.button("Run analysis!"):
    data = []
    with st.spinner("Downloading and analyzing data..."):
        for t in selected_tickers:
            d = get_stock_data(t)
            data.append(d)
    df = pd.DataFrame(data)
    st.success(f"{df.shape[0]} stocks analyzed.")

    st.markdown("#### Summary table of collected data:")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ---- FILTERING CRITERIA ----
    crit = (
        (df['P/E'] < per_max) &
        (df['P/B'] < pb_max) &
        (df['Debt/Equity'] < dette_max) &
        (df['Dividend Yield (%)'] > div_min) &
        (df['Net Profit >0']) &
        (df['Market Cap (Bn €)'] > cap_min)
    )
    filtres_df = df[crit]

    st.markdown("### Stocks that meet your Graham criteria:")
    st.dataframe(filtres_df, use_container_width=True, hide_index=True)

    # --- Export CSV
    if not filtres_df.empty:
        st.download_button(
            label="Download selection (CSV)",
            data=filtres_df.to_csv(index=False).encode('utf-8'),
            file_name="graham_stocks_sbf120.csv",
            mime="text/csv"
        )
    else:
        st.info("No stock meets all the chosen criteria.")

    # --- Visualization
    if not filtres_df.empty:
        st.subheader("Price of selected stocks")
        st.line_chart(filtres_df.set_index("Name")["Price"])

    st.markdown(f"""
    #### Main Applied Graham Criteria
    - **P/E < {per_max}**
    - **P/B < {pb_max}**
    - **Debt/Equity < {dette_max}%**
    - **Dividend yield > {div_min}%**
    - **Positive net profit**
    - **Market cap > {cap_min} Bn €**
    """)
else:
    st.warning("Select companies and click the button to start.")
