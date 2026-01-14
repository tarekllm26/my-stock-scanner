import streamlit as st
import finnhub
import time

# --- SETUP ---
# Replace 'YOUR_API_KEY' with your actual Finnhub key
finnhub_client = finnhub.Client(api_key='d5j4d59r01qh37ui8e10d5j4d59r01qh37ui8e1g')

st.title("My Triple Stock Scanner")
st.write("Refreshing every 30 seconds...")

# List of symbols you want to track
symbols = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'AMZN', 'GOOGL']

# --- THE 3 SCANNERS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.header("Price Gainers")
    st.caption("Over 2% up today")

with col2:
    st.header("High Volume")
    st.caption("Active tickers")

with col3:
    st.header("Dip Buy")
    st.caption("Down more than 3%")

# --- LOGIC LOOP ---
def run_scanners():
    for symbol in symbols:
        try:
            quote = finnhub_client.quote(symbol)
            price = quote['c']  # Current Price
            percent_change = quote['dp'] # Daily percent change

            # Scanner 1: Gainers
            if percent_change > 2:
                col1.success(f"{symbol}: ${price} (+{percent_change}%)")

            # Scanner 3: Losers/Dips
            if percent_change < -3:
                col3.error(f"{symbol}: ${price} ({percent_change}%)")
                
            # Scanner 2: Basic Price Monitor (All others)
            if -3 <= percent_change <= 2:
                col2.info(f"{symbol}: ${price}")
        except:
            pass

run_scanners()

# Auto-refresh the page
time.sleep(30)
st.rerun()
