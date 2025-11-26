# Graham Screener for the SBF120

A **Streamlit** application for screening French stocks in the **SBF120** index using Graham’s value investing methodology. This interactive tool helps both beginners and professionals identify value opportunities via customizable, time-tested fundamental criteria. It includes real-time updates for bonds and crypto rates alongside summary statistics and CSV export.

## Features

- **Up-to-date Selection:** Instantly screen the entire SBF120 using the real names and tickers of top French stocks.
- **Graham’s Criteria:** Visual, adjustable filters for:
  - Price/Earnings Ratio (PER)
  - Price/Book Ratio (P/B)
  - Debt/Equity Ratio
  - Dividend Yield (%)
  - Minimum Market Capitalization
  - Positive Net Income
- **Live Market Data:** Real-time display of:
  - US, France, Germany 10Y government bond yields
  - BTC/USD and ETH/USD prices
- **Custom Selections & Analysis:** Choose any combination of stocks for custom analysis.
- **Easy Export:** Download your filtered selection in CSV format.
- **Simple Visualization:** Line charts for selected stock prices.
- **User Guidance:** Integrated help and explanations for each criterion directly in the UI.

## How Does It Work?

1. **Select stocks** to analyze via the interactive multi-select widget.
2. **Adjust Graham’s criteria** via intuitive sliders with embedded help.
3. **Launch the analysis** to fetch the latest data (valuation ratios, profitability, dividend, etc.) directly from Yahoo Finance.
4. **Results Table:** View a complete summary of your selection, automatically filtered according to your chosen thresholds.
5. **Download your screener output** as a CSV, or visualize price evolution.

## Technologies Used

- Python (Pandas, NumPy)
- Streamlit (for UI/web app)
- yfinance (for real-time data)
- certifi (for SSL compatibility)

## Getting Started

1. Clone this repository.
2. Install requirements:  
   `pip install -r requirements.txt
3. Run the app:  
   `streamlit run app.py`
4. Open your browser at the given local address.

---

### Example Screenshots

<!-- FOr now, I have issue with ssl certification ; so the screenshots will come later -->

---

### Background

This project is inspired by Benjamin Graham’s classic principles for value investing—a method proven to build long-term wealth. The screener adapts his evergreen rules to modern French securities and European market data.
