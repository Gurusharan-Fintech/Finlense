# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# ============ Page Config ============
st.set_page_config(page_title="FinLens AI", layout="wide")

# ============ CSS Loader ============
try:
    with open("Styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ Styles.css not found. Using default Streamlit theme.")

# ============ Helper Functions ============

def load_data(ticker):
    """Fetch ticker object and historical stock data."""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="1y")
        return t, hist
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {e}")
        return None, pd.DataFrame()

def get_company_news(ticker):
    """Fetch company news via yfinance (fallback if unavailable)."""
    try:
        t = yf.Ticker(ticker)
        news = t.news
        return news if news else []
    except Exception as e:
        return [{"title": "News unavailable", "publisher": str(e)}]

def format_number(n):
    """Safely format large numbers with commas."""
    try:
        return f"{n:,}"
    except Exception:
        return "N/A"

# ============ App Layout ============

st.title("📊 FinLens AI — The Next Generation's Financial Analyst")

# Sidebar inputs
st.sidebar.header("🔍 Company Search")
ticker = st.sidebar.text_input("Enter Company Ticker (e.g. AAPL, TSLA, MSFT)", "AAPL")

# Main content
if ticker:
    t, hist = load_data(ticker)

    if t:
        info = t.info

        # Company Overview
        st.subheader("🏢 Company Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Market Cap", format_number(info.get("marketCap")))
        col2.metric("Forward P/E", info.get("forwardPE", "N/A"))
        col3.metric("Beta", info.get("beta", "N/A"))

        st.write(info.get("longBusinessSummary", "No description available."))

        # Stock Price History
        st.subheader("📈 Stock Price History (1Y)")
        if not hist.empty:
            st.line_chart(hist["Close"])
        else:
            st.warning("No historical data available.")

        # Latest News
        st.subheader("📰 Latest News")
        news_items = get_company_news(ticker)
        if news_items:
            for n in news_items[:5]:
                st.write(f"- **{n['title']}** ({n.get('publisher', 'Unknown')})")
        else:
            st.info("No recent news found.")

        # Storytelling Analogies
        st.subheader("🎭 Storytelling Mode")
        analogy_mode = st.selectbox(
            "Explain finance using:",
            ["Default", "Cars", "Sports", "Gaming", "Fashion"]
        )

        if analogy_mode == "Cars":
            st.info(f"{ticker} is like a car brand — Market Cap is its horsepower, "
                    f"and stock volatility is the handling on sharp turns.")
        elif analogy_mode == "Sports":
            st.info(f"{ticker} is like a sports team — Revenue is its score, "
                    f"and expenses are fouls holding it back.")
        elif analogy_mode == "Gaming":
            st.info(f"{ticker} is like a video game — Profit margins are the XP you gain, "
                    f"and competitors are boss fights.")
        elif analogy_mode == "Fashion":
            st.info(f"{ticker} is like a fashion label — Brand value is its runway presence, "
                    f"and innovation is this season's collection.")
        else:
            st.write("Switch analogy mode to see finance explained in fun ways!")

else:
    st.info("Enter a company ticker in the sidebar to begin.")
