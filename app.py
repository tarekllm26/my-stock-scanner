import streamlit as st
import finnhub
import pandas as pd
import time

# --- INITIAL SETUP ---
API_KEY = 'd5j4d59r01qh37ui8e10d5j4d59r01qh37ui8e1g' # Replace with your actual key
finnhub_client = finnhub.Client(api_key=d5j4d59r01qh37ui8e10d5j4d59r01qh37ui8e1g)

# --- SHARIA & FINANCIAL FILTERS ---
def check_sharia_compliance(symbol):
    try:
        # Fetch fundamental data
        fundamentals = finnhub_client.company_basic_financials(symbol, 'all')
        metrics = fundamentals.get('metric', {})
        
        # 1. Get Debt and Market Cap
        total_debt = metrics.get('totalDebtAnnual', 0)
        market_cap = metrics.get('marketCapitalization', 0)
        
        if market_cap == 0: return False, 0
        
        # 2. Calculate Ratio (Debt to Market Cap)
        debt_ratio = (total_debt / market_cap) * 100
        
        # 3. Rule: Debt must be < 33.3%
        is_compliant = debt_ratio < 33.3
        return is_compliant, round(debt_ratio, 2)
    except Exception:
        return False, 0

def get_stock_data(symbol):
    try:
        profile = finnhub_client.company_profile2(symbol=symbol)
        quote = finnhub_client.quote(symbol)
        
        sector = profile.get('finnhubIndustry', 'N/A')
        allowed_sectors = ['Health', 'Life Sciences', 'Energy', 'Technology', 'Pharmaceuticals']
        price = quote['c']
        
        # Sector and Price Filter ($0.5 - $80)
        if any(s in sector for s in allowed_sectors) and (0.5 <= price <= 80):
            # Live Sharia Check
            is_sharia, d_ratio = check_sharia_compliance(symbol)
            
            if is_sharia:
                return {
                    "Ticker": symbol,
                    "Sector": sector,
                    "Price": price,
                    "Debt Ratio": f"{d_ratio}%",
                    "Change %": quote['dp'],
                    "High": quote['h'],
                    "Low": quote['l']
                }
    except:
        return None
    return None

# --- STRATEGY CALCULATIONS ---
def get_levels(price, strategy_type):
    if strategy_type == "Ross":
        stop = price * 0.97  # 3% stop
        tp = price * 1.10    # 10% target
    else:
        stop = price * 0.985 # 1.5% stop
        tp = price * 1.04    # 4% target
    return round(price, 2), round(stop, 2), round(target, 2)

# --- MULTI-PAGE UI ---
st.set_page_config(page_title="Islamic Day Trading Scanner", layout="wide")
st.sidebar.title("Trading Strategies")
page = st.sidebar.radio("Select Strategy", ["Andrew Aziz", "Ross Cameron", "Martin Luk"])

st.title(f"🔍 {page} Strategy Scanner")
st.info("Filtering: $0.5-$80 | Sharia Compliant (Debt < 33%) | Energy, Tech, Health, Pharma")

# Add more symbols relevant to your sectors here
SYMBOLS = ['AMD', 'NVDA', 'PFE', 'XOM', 'MRNA', 'AMD', 'FSLR', 'ENPH', 'BIIB', 'HAL', 'SLB']

results = []
with st.spinner('Scanning Market Data...'):
    for sym in SYMBOLS:
        data = get_stock_data(sym)
        if data:
            # Apply Strategy-Specific Technical Filters
            if page == "Andrew Aziz" and abs(data['Change %']) > 2:
                results.append(data)
            elif page == "Ross Cameron" and data['Change %'] > 4:
                results.append(data)
            elif page == "Martin Luk" and abs(data['Change %']) > 1:
                results.append(data)

# Show Results
if results:
    df = pd.DataFrame(results).sort_values(by="Change %", ascending=False).head(10)
    # Add Entry/Exit Columns
    df['Entry'] = df['Price']
    df['Stop Loss'] = df['Price'].apply(lambda x: round(x * 0.98, 2))
    df['Take Profit'] = df['Price'].apply(lambda x: round(x * 1.05, 2))
    
    st.table(df[['Ticker', 'Sector', 'Debt Ratio', 'Price', 'Entry', 'Stop Loss', 'Take Profit']])
else:
    st.warning("No stocks currently match all criteria. The markets might be quiet or symbols are non-compliant.")

time.sleep(60)
st.rerun()
