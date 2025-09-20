import streamlit as st
import yfinance as yf

ticker = st.session_state.get("selected_ticker", "AAPL")
st.title(f"🎮 Storytelling Mode for {ticker}")
st.write("Here goes your storytelling logic…")


