# app.py

import streamlit as st
import yfinance as yf
import pandas as pd
from textblob import TextBlob
import requests

# ================= PAGE CONFIG =================
st.set_page_config(page_title="FinLens AI", page_icon="📈", layout="wide")

# ================= LOAD CUSTOM CSS =================
with open("Styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ================= HELPER FUNCTIONS =================
def load_data(ticker, period="1y", interval="1d"):
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period, interval=interval)
        return t, hist
    except Exception as e:
        st.error(f"⚠️ Could not fetch stock data: {e}")
        return None, pd.DataFrame()

def get_company_news(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker}"
        response = requests.get(url).json()
        if "news" in response:
            return response["news"]
        else:
            return []
    except Exception as e:
        return [{"title": "News unavailable", "publisher": str(e)}]

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Settings")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, MSFT)", "AAPL")
period = st.sidebar.selectbox("Select Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])
interval = st.sidebar.selectbox("Select Interval", ["1d", "1wk", "1mo"])

# ================= MAIN APP =================
st.title("📊 FinLens AI — The Next Generation's Financial Analyst")
st.markdown("**Making Wall Street a Walk Down Your Street 🚀**")

if ticker:
    t, hist = load_data(ticker, period, interval)
    if t is not None and not hist.empty:
        try:
            info = t.get_info()
        except:
            info = t.info

        # Create Tabs
        tab1, tab2, tab3, tab4 = st.tabs(
            ["🏢 Company Overview", "📈 Trends", "📰 News & Sentiment", "🎭 Storytelling"]
        )

        # --- TAB 1: Company Overview ---
        with tab1:
            st.subheader(f"🏢 {info.get('longName', ticker)} Overview")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Market Cap", f"${info.get('marketCap', 'N/A'):,}" if info.get("marketCap") else "N/A")
            col2.metric("Revenue", f"${info.get('totalRevenue', 'N/A'):,}" if info.get("totalRevenue") else "N/A")
            col3.metric("P/E Ratio", round(info.get("trailingPE", 0), 2) if info.get("trailingPE") else "N/A")
            col4.metric("EPS", round(info.get("trailingEps", 0), 2) if info.get("trailingEps") else "N/A")

        # --- TAB 2: Trends ---
        with tab2:
            st.subheader("📈 Stock Price Trends")
            st.line_chart(hist["Close"])

            # Moving Averages
            hist["MA20"] = hist["Close"].rolling(window=20).mean()
            hist["MA50"] = hist["Close"].rolling(window=50).mean()
            st.line_chart(hist[["Close", "MA20", "MA50"]])

        # --- TAB 3: News & Sentiment ---
        with tab3:
            st.subheader(f"📰 Recent News on {ticker}")
            news_items = get_company_news(ticker)

            if news_items:
                for n in news_items[:5]:
                    title = n.get("title", "No title available")
                    publisher = n.get("publisher", "Unknown")
                    link = n.get("link", None)

                    # Sentiment Analysis
                    sentiment = TextBlob(title).sentiment.polarity
                    sentiment_label = "😊 Positive" if sentiment > 0 else "😐 Neutral" if sentiment == 0 else "😡 Negative"

                    if link:
                        st.write(f"- **[{title}]({link})** ({publisher}) → {sentiment_label}")
                    else:
                        st.write(f"- **{title}** ({publisher}) → {sentiment_label}")
            else:
                st.info("No recent news found.")

        # --- TAB 4: Storytelling ---
        with tab4:
            st.subheader("🎭 Storytelling Mode — Finance, but Fun!")

            pe = info.get("trailingPE", None)
            debt = info.get("totalDebt", None)
            mc = info.get("marketCap", None)

            if pe:
                if pe > 40:
                    st.write("🚀 This stock is like a **supercar at full speed** – thrilling but risky to handle.")
                elif pe < 10:
                    st.write("🛠️ This company is a **reliable Toyota** – steady, undervalued, and built to last.")
                else:
                    st.write("⚖️ Balanced vibes – like a gamer with both skill **and** good ping 🎮⚡.")

            if debt and mc:
                if debt > mc * 0.5:
                    st.write("💸 Heavy debt – like carrying 4 teammates in Valorant 🎯.")
                else:
                    st.write("✅ Debt under control – like a pro gamer who reloads at the right time 🔫.")

            st.info("These analogies are **rule-based** for now. Future versions will use AI storytelling 🎤.")

        # END SUCCESS MESSAGE
        st.success("✅ FinLens AI Dashboard Ready")
