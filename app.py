import streamlit as st
import yfinance as yf
import pandas as pd
from textblob import TextBlob

def load_css(file_name: str):
    """Load external CSS file into the Streamlit app"""
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ Styles.css not found, using default styling.")

# -------------------- APP CONFIG --------------------
st.set_page_config(page_title="FinLens AI", page_icon="📈", layout="wide")
load_css("Styles.css")

# -------------------- HEADER --------------------
st.markdown(
    """
    <div class="header-container">
        <h1>📊 FinLens AI</h1>
        <p>Making Wall Street a Walk Down Your Street 🚀</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- MAIN STOCK SEARCH --------------------
st.markdown('<div class="search-label">🔍 Enter a Stock to Begin:</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    ticker = st.text_input(
        "",
        "AAPL",
        key="main_ticker",
        placeholder="e.g., TSLA, MSFT, NVDA",
        label_visibility="collapsed"
    )

with col2:
    period = st.selectbox(
        "",
        ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3,
        key="main_period",
        label_visibility="collapsed"
    )

with col3:
    interval = st.selectbox(
        "",
        ["1d", "1wk", "1mo"],
        index=0,
        key="main_interval",
        label_visibility="collapsed"
    )

st.markdown("<hr>", unsafe_allow_html=True)

# -------------------- FETCH DATA --------------------
try:
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)
    info = stock.info
except Exception as e:
    st.error(f"⚠️ Could not fetch data: {e}")
    st.stop()

# -------------------- NAVIGATION TABS --------------------
st.subheader("📌 Choose Your Mode")
tab1, tab2, tab3, tab4 = st.tabs([
    "🎮 Storytelling",
    "📑 PPT Generator",
    "🧩 Analogies",
    "📊 Professional Data & Trends"
])

# -------------------- TAB CONTENT --------------------
with tab1:
    st.subheader("Gen Z Storytelling Mode 🎮✨")
    st.info("Rule-based analogies here (future: AI-powered storytelling).")

with tab2:
    st.subheader("PPT Generator 📝")
    st.info("Future feature: Generate clean financial PPTs automatically.")

with tab3:
    st.subheader("Fun Analogies 🧩")
    st.info("Rule-based analogies for finance using gaming, cars, sports, etc.")

with tab4:
    st.subheader(f"Company Overview: {info.get('longName', ticker)}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}" if info.get("marketCap") else "N/A")
    col2.metric("Revenue", f"${info.get('totalRevenue', 'N/A'):,}" if info.get("totalRevenue") else "N/A")
    col3.metric("P/E Ratio", round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else "N/A")
    col4.metric("EPS", round(info.get("trailingEps", 0), 2) if info.get("trailingEps") else "N/A")

    st.subheader("📈 Stock Price Trends")
    st.line_chart(hist["Close"])

    hist["MA20"] = hist["Close"].rolling(window=20).mean()
    hist["MA50"] = hist["Close"].rolling(window=50).mean()
    st.line_chart(hist[["Close", "MA20", "MA50"]])

    st.subheader(f"📰 Recent News on {ticker}")
    st.info("News + sentiment analysis goes here.")
