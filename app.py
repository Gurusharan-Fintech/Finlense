# app.py

import streamlit as st
import yfinance as yf
import pandas as pd
from textblob import TextBlob
import requests

# ================= PAGE CONFIG =================
st.set_page_config(page_title="FinLens AI", page_icon="📈", layout="wide")

# ================= LOAD CUSTOM CSS =================
try:
    with open("Styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ Styles.css not found. Default theme will be used.")

# ================= SESSION NAVIGATION =================
if "page" not in st.session_state:
    st.session_state.page = "home"


def navigate(page):
    """Handles navigation between pages"""
    st.session_state.page = page


# ================= HOME PAGE =================
if st.session_state.page == "home":
    st.markdown(
        """
        <div class="hero">
            <h1>📊 FinLens AI</h1>
            <p>The Next Generation's Financial Analyst 🚀</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button("📑 PPT Generator", use_container_width=True):
            navigate("ppt")
        if st.button("🧩 Fun Analogies", use_container_width=True):
            navigate("analogies")
    with col2:
        if st.button("🎬 Video Mode", use_container_width=True):
            navigate("videos")
        if st.button("📊 Pro Dashboard", use_container_width=True):
            navigate("dashboard")

# ================= PPT GENERATOR PAGE =================
elif st.session_state.page == "ppt":
    st.title("📑 PPT Generator")
    st.info("⚡ Coming soon: Generate pitch-deck style slides automatically!")

    if st.button("⬅ Back Home"):
        navigate("home")

# ================= VIDEO PAGE =================
elif st.session_state.page == "videos":
    st.title("🎬 Video Generator")
    st.write("Choose your style:")

    col1, col2 = st.columns(2)
    with col1:
        st.button("🎥 Professional Explainer", use_container_width=True)
    with col2:
        st.button("🔥 Brainrot / TikTok Style", use_container_width=True)

    if st.button("⬅ Back Home"):
        navigate("home")

# ================= ANALOGIES PAGE =================
elif st.session_state.page == "analogies":
    st.title("🧩 Storytelling & Analogies")
    st.write("👉 Example: Tesla is the student who **aces math but forgets homework** 🤓📉")
    st.write("👉 Example: Apple is like the **friend who flexes the newest iPhone** 🍏📱")
    st.write("👉 Example: A high P/E stock is a **supercar at full speed** 🚗💨")

    if st.button("⬅ Back Home"):
        navigate("home")

# ================= DASHBOARD PAGE =================
elif st.session_state.page == "dashboard":
    st.title("📊 Professional Dashboard")

    # Sidebar Inputs
    ticker = st.sidebar.text_input("Enter Stock Ticker", "AAPL")
    period = st.sidebar.selectbox(
        "Select Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
    )
    interval = st.sidebar.selectbox(
        "Select Interval", ["1d", "1wk", "1mo"]
    )

    def load_data(ticker, period, interval):
        """Fetches stock data"""
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period=period, interval=interval)
            return t, hist
        except Exception as e:
            st.error(f"⚠️ Could not fetch stock data: {e}")
            return None, pd.DataFrame()

    # Load Data
    t, hist = load_data(ticker, period, interval)

    if t and not hist.empty:
        # Try fetching company info
        try:
            info = t.get_info()
        except Exception:
            info = getattr(t, "info", {})

        # Company Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(
            "Market Cap",
            f"${info.get('marketCap', 'N/A'):,}" if info.get("marketCap") else "N/A",
        )
        col2.metric(
            "Revenue",
            f"${info.get('totalRevenue', 'N/A'):,}"
            if info.get("totalRevenue")
            else "N/A",
        )
        col3.metric(
            "P/E Ratio",
            round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else "N/A",
        )
        col4.metric(
            "EPS",
            round(info.get("trailingEps", 0), 2) if info.get("trailingEps") else "N/A",
        )

        # Stock Price Chart
        st.subheader("📈 Stock Price Trends")
        st.line_chart(hist["Close"])

        # Moving Averages
        hist["MA20"] = hist["Close"].rolling(window=20).mean()
        hist["MA50"] = hist["Close"].rolling(window=50).mean()
        st.line_chart(hist[["Close", "MA20", "MA50"]])

        # News & Sentiment
        st.subheader("📰 News & Sentiment")
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker}"
        try:
            response = requests.get(url).json()
            if "news" in response:
                for article in response["news"][:5]:
                    title = article.get("title", "No title available")
                    link = article.get("link", None)
                    sentiment = TextBlob(title).sentiment.polarity
                    sentiment_label = (
                        "😊 Positive" if sentiment > 0 else
                        "😐 Neutral" if sentiment == 0 else
                        "😡 Negative"
                    )
                    if link:
                        st.write(f"- **[{title}]({link})** → {sentiment_label}")
                    else:
                        st.write(f"- **{title}** → {sentiment_label}")
            else:
                st.info("No news found.")
        except Exception:
            st.error("⚠️ Could not fetch news.")

    else:
        st.warning("Enter a valid ticker to see stock data.")

    if st.button("⬅ Back Home"):
        navigate("home")
