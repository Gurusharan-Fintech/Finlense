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
    "Select Inter
