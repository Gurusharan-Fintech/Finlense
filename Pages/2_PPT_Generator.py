import streamlit as st

ticker = st.session_state.get("selected_ticker", "AAPL")
st.title(f"📑 PPT Generator for {ticker}")
st.info("Future feature: Generate clean financial PPTs automatically.")

