import streamlit as st
import yfinance as yf
import datetime
import requests
from textblob import TextBlob
import pandas as pd

# Load CSS from styles.css
def load_css(styles.css: str):
    with open(styles.css) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Call the function and pass your CSS file
load_css("styles.css")

# -------------------- APP CONFIG --------------------
st.set_page_config(page_title="FinLens AI", page_icon="📈", layout="wide")

st.title("📊 FinLens AI - Your Gen Z Finance Lens")
st.markdown("**Making Wall Street a Walk Down Your Street 🚀**")
# -------------------- APP CONFIG --------------------
st.set_page_config(page_title="FinLens AI", page_icon="📈", layout="wide")

st.title("📊 FinLens AI - Your Gen Z Finance Lens")
st.markdown("**Making Wall Street a Walk Down Your Street 🚀**")


# -------------------- SIDEBAR --------------------
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, MSFT)", "AAPL")
period = st.sidebar.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])
interval = st.sidebar.selectbox("Select Interval", ["1d", "1wk", "1mo"])


# -------------------- FETCH DATA --------------------
try:
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)

    # Company info
    info = stock.info
except Exception as e:
    st.error(f"⚠️ Could not fetch data: {e}")
    st.stop()

# -------------------- TABS --------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Company Overview", "📉 Trends", "📰 Sentiment", "🎮 Storytelling"])

# -------------------- TAB 1: COMPANY OVERVIEW --------------------
with tab1:
    st.subheader(f"Company Overview: {info.get('longName', ticker)}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}")
    col2.metric("Revenue", f"${info.get('totalRevenue', 'N/A'):,}" if info.get("totalRevenue") else "N/A")
    col3.metric("P/E Ratio", round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else "N/A")
    col4.metric("EPS", round(info.get("trailingEps", 0), 2) if info.get("trailingEps") else "N/A")

# -------------------- TAB 2: TRENDS --------------------
with tab2:
    st.subheader("Stock Price Trends")

    st.line_chart(hist["Close"])

    # Add moving averages
    hist["MA20"] = hist["Close"].rolling(window=20).mean()
    hist["MA50"] = hist["Close"].rolling(window=50).mean()
    st.line_chart(hist[["Close", "MA20", "MA50"]])

# -------------------- TAB 3: NEWS & SENTIMENT --------------------
with tab3:
    st.subheader(f"Recent News on {ticker}")

    # Free Yahoo Finance news API (unofficial)
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker}"
    try:
        response = requests.get(url).json()
        if "news" in response:
            news_list = response["news"][:5]
            for article in news_list:
                title = article.get("title", "")
                link = article.get("link", "")
                sentiment = TextBlob(title).sentiment.polarity
                sentiment_label = "😊 Positive" if sentiment > 0 else "😐 Neutral" if sentiment == 0 else "😡 Negative"
                st.write(f"**[{title}]({link})** → Sentiment: {sentiment_label}")
        else:
            st.info("No news found.")
    except:
        st.error("Could not fetch news at the moment.")

# -------------------- TAB 4: STORYTELLING --------------------
with tab4:
    st.subheader("Gen Z Storytelling Mode 🎮✨")

    pe = info.get("trailingPE", None)
    debt = info.get("totalDebt", None)
    mc = info.get("marketCap", None)

    if pe:
        if pe > 40:
            st.write("📈 This stock is like a **supercar at full speed** – exciting but might crash anytime 🚗💨.")
        elif pe < 10:
            st.write("🛠️ This company is like a **reliable old Toyota** – not flashy, but steady and undervalued 🚙.")
        else:
            st.write("⚖️ Balanced vibes – like a gamer with both skill **and** good ping 🎮⚡.")

    if debt:
        if debt > mc * 0.5:
            st.write("💸 This company’s debt is heavy – like carrying 4 teammates in Valorant 🎯.")
        else:
            st.write("✅ Debt under control – like a pro gamer who knows when to reload 🔫.")

    st.info("These are **rule-based analogies** for now. Future versions will use AI storytelling models 🎤.")

# -------------------- END --------------------
st.success("FinLens AI Lite Ready ✅")
=======

# -------------------- FETCH DATA --------------------
try:
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period, interval=interval)

    # Company info
    info = stock.info
except Exception as e:
    st.error(f"⚠️ Could not fetch data: {e}")
    st.stop()

# -------------------- TABS --------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Company Overview", "📉 Trends", "📰 Sentiment", "🎮 Storytelling"])

# -------------------- TAB 1: COMPANY OVERVIEW --------------------
with tab1:
    st.subheader(f"Company Overview: {info.get('longName', ticker)}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}")
    col2.metric("Revenue", f"${info.get('totalRevenue', 'N/A'):,}" if info.get("totalRevenue") else "N/A")
    col3.metric("P/E Ratio", round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else "N/A")
    col4.metric("EPS", round(info.get("trailingEps", 0), 2) if info.get("trailingEps") else "N/A")

# -------------------- TAB 2: TRENDS --------------------
with tab2:
    st.subheader("Stock Price Trends")

    st.line_chart(hist["Close"])

    # Add moving averages
    hist["MA20"] = hist["Close"].rolling(window=20).mean()
    hist["MA50"] = hist["Close"].rolling(window=50).mean()
    st.line_chart(hist[["Close", "MA20", "MA50"]])

# -------------------- TAB 3: NEWS & SENTIMENT --------------------
with tab3:
    st.subheader(f"Recent News on {ticker}")

    # Free Yahoo Finance news API (unofficial)
    url = f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker}"
    try:
        response = requests.get(url).json()
        if "news" in response:
            news_list = response["news"][:5]
            for article in news_list:
                title = article.get("title", "")
                link = article.get("link", "")
                sentiment = TextBlob(title).sentiment.polarity
                sentiment_label = "😊 Positive" if sentiment > 0 else "😐 Neutral" if sentiment == 0 else "😡 Negative"
                st.write(f"**[{title}]({link})** → Sentiment: {sentiment_label}")
        else:
            st.info("No news found.")
    except:
        st.error("Could not fetch news at the moment.")

# -------------------- TAB 4: STORYTELLING --------------------
with tab4:
    st.subheader("Gen Z Storytelling Mode 🎮✨")

    pe = info.get("trailingPE", None)
    debt = info.get("totalDebt", None)
    mc = info.get("marketCap", None)

    if pe:
        if pe > 40:
            st.write("📈 This stock is like a **supercar at full speed** – exciting but might crash anytime 🚗💨.")
        elif pe < 10:
            st.write("🛠️ This company is like a **reliable old Toyota** – not flashy, but steady and undervalued 🚙.")
        else:
            st.write("⚖️ Balanced vibes – like a gamer with both skill **and** good ping 🎮⚡.")

    if debt:
        if debt > mc * 0.5:
            st.write("💸 This company’s debt is heavy – like carrying 4 teammates in Valorant 🎯.")
        else:
            st.write("✅ Debt under control – like a pro gamer who knows when to reload 🔫.")

    st.info("These are **rule-based analogies** for now. Future versions will use AI storytelling models 🎤.")

# -------------------- END --------------------
st.success("FinLens AI Lite Ready ✅")


