import streamlit as st
import yfinance as yf
import requests
from textblob import TextBlob
import pandas as pd

def load_css(file_name: str):
    """Load external CSS file into the Streamlit app"""
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------- APP CONFIG --------------------
st.set_page_config(page_title="FinLens AI", page_icon="📈", layout="wide")
load_css("Styles.css")

# -------------------- HEADER --------------------
st.title("📊 FinLens AI - Your Gen Z Finance Lens")
st.markdown("**Making Wall Street a Walk Down Your Street 🚀**")

# -------------------- MAIN STOCK INPUT --------------------
st.subheader("🔍 Start by choosing a stock")

ticker = st.text_input(
    "Enter Stock Ticker (e.g., AAPL, TSLA, MSFT)",
    "AAPL",
    key="main_ticker"
)

period = st.selectbox(
    "Select Period",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=3,
    key="main_period"
)

interval = st.selectbox(
    "Select Interval",
    ["1d", "1wk", "1mo"],
    index=0,
    key="main_interval"
)

# -------------------- FETCH DATA --------------------
try:
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    info = stock.info
except Exception as e:
    st.error(f"⚠️ Could not fetch data: {e}")
    st.stop()

# -------------------- NAVIGATION TABS --------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🎮 Storytelling",
    "📑 PPT Generator",
    "🧩 Analogies",
    "📊 Professional Data & Trends"
])

# -------------------- TAB CONTENT --------------------
with tab1:
    st.subheader("Gen Z Storytelling Mode 🎮✨")
    st.info("Storytelling logic goes here.")

with tab2:
    st.subheader("PPT Generator 📝")
    st.info("Future feature: Generate clean financial PPTs automatically.")

with tab3:
    st.subheader("Fun Analogies 🧩")
    st.info("Analogy logic goes here.")

with tab4:
    st.subheader(f"Company Overview: {info.get('longName', ticker)}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}")
    col2.metric("Revenue", f"${info.get('totalRevenue', 'N/A'):,}" if info.get("totalRevenue") else "N/A")
    col3.metric("P/E Ratio", round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else "N/A")
    col4.metric("EPS", round(info.get("trailingEps", 0), 2) if info.get("trailingEps") else "N/A")

    st.subheader("📈 Stock Price Trends")
    st.line_chart(hist["Close"])

    hist["MA20"] = hist["Close"].rolling(window=20).mean()
    hist["MA50"] = hist["Close"].rolling(window=50).mean()
    st.line_chart(hist[["Close", "MA20", "MA50"]])

    st.subheader(f"📰 Recent News on {ticker}")
    st.info("News fetching logic goes here.")

st.success("✅ Ready – Pick your mode above!")
