# app.py
import streamlit as st
import yfinance as yf
import requests
from textblob import TextBlob
import pandas as pd
import numpy as np
from datetime import datetime


# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="FinLens AI", page_icon="📈", layout="wide")


# Inject CSS
with open("Styles.css", "r") as f:
st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# -------------------- HELPERS --------------------
@st.cache_data(show_spinner=False)
def fetch_history(ticker: str, period: str, interval: str):
t = yf.Ticker(ticker)
hist = t.history(period=period, interval=interval)
return hist


@st.cache_data(show_spinner=False)
def fetch_info(ticker: str):
t = yf.Ticker(ticker)
# try modern method first
try:
info = t.get_info()
except Exception:
info = t.info if hasattr(t, "info") else {}
return info


@st.cache_data(show_spinner=False)
def fetch_news_via_yf(ticker: str):
t = yf.Ticker(ticker)
try:
news = t.news
return news
except Exception:
# fallback to Yahoo search
url = f"https://query1.finance.yahoo.com/v1/finance/search?q={ticker}"
try:
resp = requests.get(url, timeout=6).json()
return resp.get("news", [])
except Exception:
return []




def nice_num(x):
try:
if x is None:
return "N/A"
if abs(x) >= 1_000_000_000:
return f"${x/1_000_000_000:,.2f}B"
if abs(x) >= 1_000_000:
return f"${x/1_000_000:,.2f}M"
if abs(x) >= 1_000:
return f"${x/1_000:,.2f}K"
return f"${x:,.2f}"
except Exception:
return "N/A"




def sentiment_label(score: float):
if score > 0.1:
return "Positive 😊"
if score < -0.1:
return "Negative 😡"
 unsafe_allow_html=True)
