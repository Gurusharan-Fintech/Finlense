import streamlit as st

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

# -------------------- UNIFIED SEARCH BOX --------------------
st.subheader("🔎 Start by choosing a stock")

ticker_choice = st.selectbox(
    "Enter Stock Ticker (search or select):",
    options=[""] + list(stock_options.values()) + list(stock_options.keys()),
    index=0,
    placeholder="Type or select a stock (e.g., AAPL, RELIANCE.NS)...",
)

if ticker_choice in stock_options:
    ticker = stock_options[ticker_choice]
else:
    ticker = ticker_choice if ticker_choice else None

if ticker:
    st.success(f"📌 Selected Stock: **{ticker}**")
else:
    st.info("Please choose a stock to continue.")

# -------------------- BUTTON STYLING --------------------
st.markdown("### 🚀 Choose a mode")

button_css = """
<style>
div.stButton > button {
    border-radius: 12px;
    height: 60px;
    font-size: 18px;
    font-weight: 600;
    width: 100%;
    margin-top: 8px;
}
</style>
"""
st.markdown(button_css, unsafe_allow_html=True)

# -------------------- BUTTON LAYOUT --------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("🎮 Storytelling"):
        if ticker:
            st.session_state["selected_ticker"] = ticker
            st.switch_page("pages/1_Storytelling.py")
        else:
            st.error("Pick a stock first!")

    if st.button("📑 PPT Generator"):
        if ticker:
            st.session_state["selected_ticker"] = ticker
            st.switch_page("pages/2_PPT_Generator.py")
        else:
            st.error("Pick a stock first!")

with col2:
    if st.button("🧩 Analogies"):
        if ticker:
            st.session_state["selected_ticker"] = ticker
            st.switch_page("pages/3_Analogies.py")
        else:
            st.error("Pick a stock first!")

    if st.button("📊 Professional Data & Trends"):
        if ticker:
            st.session_state["selected_ticker"] = ticker
            st.switch_page("pages/4_Professional_Data.py")
        else:
            st.error("Pick a stock first!")
