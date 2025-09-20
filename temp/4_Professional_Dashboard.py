import streamlit as st
import yfinance as yf

ticker = st.session_state.get("selected_ticker", "AAPL")
st.title(f"📊 Professional Dashboard for {ticker}")

try:
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo", interval="1d")
    st.line_chart(hist["Close"])
except:
    st.error("Could not fetch stock data.")

