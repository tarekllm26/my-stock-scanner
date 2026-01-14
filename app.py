import streamlit as st
import finnhub
import pandas as pd
import time

# --- CONFIG ---
API_KEY = 'd5j4d59r01qh37ui8e10d5j4d59r01qh37ui8e1g'
finnhub_client = finnhub.Client(api_key=API_KEY)

# --- MASTER SECTOR WATCHLIST ---
# We use a focused list to ensure we don't hit the 60-call limit too fast
SECTOR_WATCHLIST = {
    "Technology": ['AMD', 'NVDA', 'PLTR', 'SNOW', 'ROKU', 'AMD', 'INTC', 'MU', 'ARM', 'TSM'],
    "Energy": ['XOM', 'CVX', 'HAL', 'SLB', 'OXY', 'FSLR', 'ENPH', 'RUN', 'VLO', 'MPC'],
    "Healthcare/Pharma": ['PFE', 'MRNA', 'BIIB', 'VRTX', 'GILD', 'AMGN', 'JNJ', 'ABBV', 'LLY', 'BMY']
}

def get_stock_data(symbol):
    try:
        # 1. Get Quote & Profile (2 calls)
        quote = finnhub_client.quote(symbol)
        profile = finnhub_client.company_profile2(symbol=symbol)
        
        price = quote['c']
        change = quote['dp']
        
        # Filter Price Range
        if not (0.5 <= price <= 80):
            return None
            
        # 2. Sharia Check (1 call)
        fundamentals = finnhub_client.company_basic_financials(symbol, 'all')
        metrics = fundamentals.get('metric', {})
        debt = metrics.get('totalDebtAnnual', 0)
        mcap = metrics.get('marketCapitalization', 0)
        debt_ratio = (debt / mcap) * 100 if mcap > 0 else 999
        
        if debt_ratio < 33.3:
            return {
                "Ticker": symbol,
                "Sector": profile.get('finnhubIndustry', 'N/A'),
                "Price": price,
                "Change %": change,
                "Debt Ratio": f"{round(debt_ratio, 1)}%",
                "Entry": price,
                "Stop": round(price * 0.98, 2),
                "Target": round(price * 1.05, 2)
            }
    except:
        return None

# --- UI SETUP ---
st.set_page_config(page_title="Sector Strategy Scanner", layout="wide")
st.title("📊 Top 10 Sector-Based Strategy Scanner")

strategy = st.sidebar.selectbox("Select Strategy", ["Andrew Aziz", "Ross Cameron", "Martin Luk"])
st.sidebar.info(f"Currently scanning {strategy} criteria...")

# --- PROCESSING ---
all_results = []
with st.spinner("Checking Sector Watchlists..."):
    for sector, symbols in SECTOR_WATCHLIST.items():
        for sym in symbols:
            data = get_stock_data(sym)
            if data:
                all_results.append(data)

# --- APPLY STRATEGY FILTERS ---
if all_results:
    df = pd.DataFrame(all_results)
    
    # Filter based on strategy rules
    if strategy == "Ross Cameron":
        # High momentum / Gappers
        df = df[df['Change %'] > 3]
    elif strategy == "Andrew Aziz":
        # Strong intraday moves
        df = df[abs(df['Change %']) > 2]
    
    # Sort by performance and take top 10
    top_10 = df.sort_values(by="Change %", ascending=False).head(10)

    # --- DISPLAY ---
    if not top_10.empty:
        st.subheader(f"Top 10 Halal Matches for {strategy}")
        st.table(top_10[['Ticker', 'Sector', 'Price', 'Change %', 'Debt Ratio', 'Entry', 'Stop', 'Target']])
    else:
        st.warning("No stocks currently meet the strategy's % change criteria.")
else:
    st.error("No stocks found matching the Sector/Price/Sharia filters.")

# --- AUTO-REFRESH ---
st.caption("Auto-refreshing every 60 seconds...")
time.sleep(60)
st.rerun()
