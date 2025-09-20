import streamlit as st
import yfinance as yf

# -------------------- APP CONFIG --------------------
st.set_page_config(page_title="FinLens AI", page_icon="📈", layout="wide")

st.title("📊 FinLens AI - Your Gen Z Finance Lens")
st.markdown("**Making Wall Street a Walk Down Your Street 🚀**")

# -------------------- STOCK LIST --------------------
nifty50 = {
    "Reliance Industries": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
}
sensex30 = {
    "State Bank of India": "SBIN.BO",
    "Tata Steel": "TATASTEEL.BO",
    "Asian Paints": "ASIANPAINT.BO",
    "Bajaj Finance": "BAJFINANCE.BO",
    "HUL": "HINDUNILVR.BO",
}
nasdaq = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Tesla": "TSLA",
    "NVIDIA": "NVDA",
}

stock_options = {**nifty50, **sensex30, **nasdaq}

# -------------------- MAIN STOCK INPUT --------------------
st.subheader("🔎 Start by choosing a stock")

col1, col2 = st.columns([2, 2])

with col1:
    dropdown_choice = st.selectbox(
        "Pick from list (NIFTY50 / SENSEX / NASDAQ):",
        options=[""] + list(stock_options.keys())
    )

with col2:
    manual_input = st.text_input("Or type a ticker symbol (e.g., RELIANCE.NS, AAPL):")

# Final ticker logic
if manual_input:
    ticker = manual_input.upper().strip()
elif dropdown_choice:
    ticker = stock_options[dropdown_choice]
else:
    ticker = None

if ticker:
    st.success(f"📌 Selected Stock: **{ticker}**")
else:
    st.info("Please choose or type a stock symbol to begin.")

# -------------------- BIG NAVIGATION BUTTONS --------------------
st.markdown("### 🚀 Choose Your Mode")

button_css = """
<style>
div.stButton > button {
    width: 100%;
    height: 100px;
    border-radius: 15px;
    font-size: 20px;
    font-weight: bold;
    margin: 10px 0;
    background-color: #0d47a1;
    color: white;
}
</style>
"""
st.markdown(button_css, unsafe_allow_html=True)

colA, colB = st.columns(2)
with colA:
    if st.button("🎮 Storytelling"):
        if ticker:
            st.session_state["selected_ticker"] = ticker
            st.switch_page("pages/1_Storytelling.py")
        else:
            st.error("Please select a stock first!")

    if st.button("🧩 Analogies"):
        if ticker:
            st.session_state["selected_ticker"] = ticker
            st.switch_page("pages/3_Analogies.py")
        else:
            st.error("Please select a stock first!")

with colB:
    if st.button("📑 PPT Generator"):
        if ticker:
            st.session_state["selected_ticker"] = ticker
            st.switch_page("pages/2_PPT_Generator.py")
        else:
            st.error("Please select a stock first!")

    if st.button("📊 Professional Dashboard"):
        if ticker:
            st.session_state["selected_ticker"] = ticker
            st.switch_page("pages/4_Professional_Data.py")
        else:
            st.error("Please select a stock first!")

