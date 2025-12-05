import os
import certifi
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor

os.environ['SSL_CERT_FILE'] = certifi.where()

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
    "ITP.PA": "Interparfums", "KER.PA": "Kering", "KORI.PA": "Korian",
    "LHA.DE": "Lufthansa", "LLD.PA": "Linedata Services", "LOIM.PA": "Laurent-Perrier",
    "LVMH.PA": "LVMH", "MDT.PA": "Medtronic", "MDG.PA": "M6-Metropole Television",
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

# -------------------------
# SESSION STATE FOR FILTERS
# -------------------------
if "sort_col" not in st.session_state:
    st.session_state["sort_col"] = 'Name'
if "sort_asc" not in st.session_state:
    st.session_state["sort_asc"] = False

# -------------------------
# YIELDS & CRYPTO UTILITIES
# -------------------------
def get_rate_yield(ticker: str) -> str:
    try:
        dta = yf.Ticker(ticker).history(period="1d")
        if len(dta) > 0:
            last = dta["Close"].iloc[-1]
            if ticker == "^TNX":  # US 10Y déjà en %
                return f"{round(float(last), 2)}"
            else:
                return f"{round(float(last) * 100, 2)}"
    except Exception:
        pass
    return "Data unavailable"

def get_asset_price(ticker: str) -> str:
    try:
        dta = yf.Ticker(ticker).history(period="1d")
        if len(dta) > 0:
            return f"{round(float(dta['Close'].iloc[-1]), 2):,}"
    except Exception:
        pass
    return "Data unavailable"

# -------------------------
# STOCK DATA FETCHING
# -------------------------
def get_stock_data(ticker: str) -> dict:
    stock = yf.Ticker(ticker)

    # Essayer de récupérer info en protégeant les erreurs
    try:
        info = stock.info
    except Exception:
        # Retour minimal si l'appel échoue complètement
        return {
            'Name': ticker,
            'Ticker': ticker,
            'Price': np.nan, 'P/E': np.nan, 'P/B': np.nan, 'Debt/Equity': np.nan,
            'Dividend Yield (%)': np.nan, 'Market Cap (Bn €)': np.nan, 'EPS': np.nan,
            'Net Profit >0': np.nan, 'Dividend/year': np.nan, 'Sector': 'N/A',
            'Industry': 'N/A', 'Description': 'N/A',
        }

    def gv(key, default=np.nan):
        v = info.get(key, default)
        if v is None:
            return default
        return v

    try:
        price = gv('currentPrice')
        pe = gv('trailingPE')
        pb = gv('priceToBook')
        debt_eq = gv('debtToEquity')
        dy = gv('dividendYield')
        mcap = gv('marketCap')
        profit_margins = gv('profitMargins')
        dividend_rate = gv('dividendRate')
        eps = gv('trailingEps')

        data = {
            'Name': gv('shortName', ticker),
            'Ticker': ticker,
            'Price': float(price) if not pd.isna(price) else np.nan,
            'P/E': float(pe) if not pd.isna(pe) else np.nan,
            'P/B': float(pb) if not pd.isna(pb) else np.nan,
            'Debt/Equity': float(debt_eq) if not pd.isna(debt_eq) else np.nan,
            'Dividend Yield (%)': float(dy) * 100 if not pd.isna(dy) else np.nan,
            'Market Cap (Bn €)': float(mcap) / 1e9 if not pd.isna(mcap) else np.nan,
            'EPS': float(eps) if not pd.isna(eps) else np.nan,
            'Net Profit >0': bool(profit_margins > 0) if not pd.isna(profit_margins) else np.nan,
            'Dividend/year': float(dividend_rate) if not pd.isna(dividend_rate) else np.nan,
            'Sector': gv('sector', 'N/A'),
            'Industry': gv('industry', 'N/A'),
            'Description': gv('longBusinessSummary', 'N/A'),
        }
    except Exception:
        data = {
            'Name': ticker,
            'Ticker': ticker,
            'Price': np.nan, 'P/E': np.nan, 'P/B': np.nan, 'Debt/Equity': np.nan,
            'Dividend Yield (%)': np.nan, 'Market Cap (Bn €)': np.nan, 'EPS': np.nan,
            'Net Profit >0': np.nan, 'Dividend/year': np.nan, 'Sector': 'N/A',
            'Industry': 'N/A', 'Description': 'N/A',
        }

    return data

# -------------------------
# MAIN APP USER INTERFACE
# -------------------------
st.set_page_config(page_title="Graham SBF120 Stock Picker", layout="wide")
st.title("Graham Stock Picker - SBF120")
with st.expander("ℹ️ How this app works / About Graham", expanded=False):
    st.write("""
    This screener ranks the SBF120 using Graham's classic value criteria.
    You can adjust filters, sort your results, explore company details, and export your picks.
    - A Graham Score is computed for each stock (the higher, the better).
    - Real-time market and crypto rates are shown above.
    """)

# -------------------------
# DISPLAY RATES AND CRYPTOS
# -------------------------
cols = st.columns(5)
cols[0].metric("US 10Y Yield", f"{get_rate_yield('^TNX')}%")

# Ces tickers FR/DE risquent de ne pas exister : garde-les ou commente-les selon ton besoin
cols[1].metric("FR 10Y Yield", f"{get_rate_yield('^FR10Y')}%")
cols[2].metric("DE 10Y Yield", f"{get_rate_yield('^DE10Y')}%")

cols[3].metric("BTC/USD", f"${get_asset_price('BTC-USD')}")
cols[4].metric("ETH/USD", f"${get_asset_price('ETH-USD')}")

st.markdown("_Screen the SBF120 using **Benjamin Graham**'s value criteria. Adjust sliders and explore!_")

# -------------------------
# GRAHAM CRITERIA SELECTION
# -------------------------
with st.expander("🔧 Selection criteria (hover for help)", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        per_max = st.slider("Maximum P/E", 5.0, 30.0, 15.0, help="Price/Earnings Ratio. Graham recommended < 15.")
        pb_max = st.slider("Maximum Price/Book", 0.5, 5.0, 1.5, help="Price/Book Ratio. Graham ideal: < 1.5.")
    with col2:
        dette_max = st.slider("Max Debt/Equity (%)", 0, 300, 100, help="Debt/Equity %. Graham: < 100%.")
        cap_min = st.slider("Minimum Market Cap (Bn €)", 0, 20, 2, help="Minimum market cap, Graham: > 2 Bn €.")
    with col3:
        div_min = st.slider("Minimum Dividend Yield (%)", 0.0, 10.0, 2.0, help="Dividend Yield, Graham: >2-3%.")

# -------------------------
# OPTIONAL FILTERS & HISTORY PERIOD
# -------------------------
with st.expander("🔎 Extra filters", expanded=False):
    period = st.selectbox(
        "Select price history period for visualization",
        ['1mo', '3mo', '6mo', '1y', 'max'],
        index=2
    )

# -------------------------
# STOCK SELECTION
# -------------------------
selected_names = st.multiselect(
    "Select the stocks to analyze",
    options=TICKER_CHOICES,
    default=TICKER_CHOICES,  # All companies pre-selected
    help="You will see the stock name and its ticker."
)
selected_tickers = [c.split("(")[-1].replace(")", "").strip() for c in selected_names]

if not selected_tickers:
    st.warning("Select at least one company to analyze.")
    st.stop()

# -------------------------
# EXECUTE ANALYSIS ON BUTTON
# -------------------------
if st.button("Run analysis!"):
    with st.spinner("Analyzing companies (async)..."):
        with ThreadPoolExecutor() as executor:
            data = list(executor.map(get_stock_data, selected_tickers))

    df = pd.DataFrame(data)

    # -------------------------
    # TICKERS AVEC PROBLÈME DE DONNÉES
    # -------------------------
    error_tickers = df[df['Price'].isna()]['Ticker'].tolist()

    # -------------------------
    # GRAHAM CRITERIA & SCORE
    # -------------------------
    pe_crit = (df['P/E'] < per_max).fillna(False)
    pb_crit = (df['P/B'] < pb_max).fillna(False)
    de_crit = (df['Debt/Equity'] < dette_max).fillna(False)
    dy_crit = (df['Dividend Yield (%)'] > div_min).fillna(False)
    np_crit = df['Net Profit >0'].fillna(False)
    mcap_crit = (df['Market Cap (Bn €)'] > cap_min).fillna(False)

    criteria = {
        'P/E': pe_crit,
        'P/B': pb_crit,
        'Debt/Equity': de_crit,
        'Dividend Yield (%)': dy_crit,
        'Net Profit >0': np_crit,
        'Market Cap (Bn €)': mcap_crit,
    }

    crit_matrix = np.column_stack(list(criteria.values()))
    df['Graham Score'] = crit_matrix.sum(axis=1)
    df['Graham Pass'] = df['Graham Score'] == len(criteria)

    # -------------------------
    # TABLE, SORT & EXPORT SETTINGS
    # -------------------------
    graham_columns = [
        'Name', 'Ticker', 'Price', 'P/E', 'P/B', 'Debt/Equity',
        'Dividend Yield (%)', 'Market Cap (Bn €)', 'EPS',
        'Dividend/year', 'Net Profit >0', 'Graham Score', 'Sector', 'Industry'
    ]

    export_columns = st.multiselect(
        "Columns to export", graham_columns, default=graham_columns[:-2]
    )

    sort_col = st.selectbox("Sort by:", graham_columns, index=graham_columns.index('Graham Score'))
    sort_asc_label = st.radio("Order:", ["Ascending", "Descending"], index=1, horizontal=True)
    sort_asc = (sort_asc_label == "Ascending")

    df = df.sort_values(by=sort_col, ascending=sort_asc)

    # -------------------------
    # DISPLAY CRITERIA SUMMARY
    # -------------------------
    st.info(
        f"**Graham criteria**: P/E < {per_max}, P/B < {pb_max}, Debt/Equity < {dette_max}%, "
        f"Dividend Yield > {div_min}%, Market Cap > {cap_min} Bn €, Net Profit > 0"
    )

    # -------------------------
    # DISPLAY MAIN DATA TABLE
    # -------------------------
    st.markdown("#### All selected companies")

    def highlight_row(row, pass_series):
        passed = pass_series.get(row.name, False)
        color = 'lightgreen' if passed else ''
        return ['background-color: %s' % color for _ in row]

    pass_series = df['Graham Pass']
    df_visible = df[graham_columns]

    st.dataframe(
        df_visible.style.apply(highlight_row, axis=1, pass_series=pass_series),
        use_container_width=True,
        hide_index=True
    )

    # -------------------------
    # DISPLAY GRAHAM-COMPLIANT STOCKS
    # -------------------------
    filtres_df = df[df['Graham Pass'] == True]
    st.markdown("### Stocks meeting **all** Graham criteria")

    if not filtres_df.empty:
        filtres_visible = filtres_df[graham_columns]
        pass_series_filtres = filtres_df['Graham Pass']

        st.dataframe(
            filtres_visible.style.apply(highlight_row, axis=1, pass_series=pass_series_filtres),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No stock meets all the chosen criteria.")

    # -------------------------
    # EXPORT FILTERED CSV
    # -------------------------
    if not filtres_df.empty:
        st.download_button(
            label="Download filtered selection (CSV)",
            data=filtres_df[export_columns].to_csv(index=False).encode('utf-8'),
            file_name="graham_stocks_sbf120.csv",
            mime="text/csv"
        )

    # -------------------------
    # ERROR REPORTING
    # -------------------------
    if error_tickers:
        with st.expander("Data unavailable for these tickers"):
            st.write(", ".join(error_tickers))

    # -------------------------
    # COMPANY DETAILS
    # -------------------------
    with st.expander("See company details / descriptions"):
        if filtres_df.empty:
            st.info("No Graham-compliant stock to display.")
        else:
            for _, row in filtres_df.iterrows():
                with st.expander(f"{row['Name']} ({row['Ticker']})"):
                    st.markdown(f"**Sector:** {row['Sector']}  \n**Industry:** {row['Industry']}")
                    st.write(row['Description'])

    # -------------------------
    # VISUALIZATION & PRICE HISTORY
    # -------------------------
    st.subheader(f"Price history ({period}) for Graham-compliant stocks")
    chart_data = pd.DataFrame()

    if not filtres_df.empty:
        for _, row in filtres_df.iterrows():
            tkr = row['Ticker']
            ticker_yf = yf.Ticker(tkr)
            try:
                hist = ticker_yf.history(period=period)
                if len(hist) > 0:
                    chart_data[row['Name']] = hist['Close']
            except Exception:
                continue

        if not chart_data.empty:
            st.line_chart(chart_data)
        else:
            st.info("No price data available for this period.")
    else:
        st.info("No Graham-compliant stocks to chart yet. Adjust criteria or run the analysis.")

else:
    st.warning("Select companies and click the button to start.")
