import streamlit as st

# -------------------- APP CONFIG --------------------
st.set_page_config(page_title="FinLens AI", page_icon="📈", layout="wide")

# -------------------- TITLE --------------------
st.markdown(
    "<h1 class='center-title'>📊 FinLens AI - Your Gen Z Finance Lens</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p class='center-title'><b>Making Wall Street a Walk Down Your Street 🚀</b></p>",
    unsafe_allow_html=True,
)

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
    st.session_state["selected_stock"] = ticker
    st.write(f"Debug: Session state set to: {st.session_state.get('selected_stock', 'Not set')}")
else:
    st.info("Please choose a stock to continue.")

# -------------------- CSS STYLING --------------------
st.markdown(
    """
    <style>
    /* ---------- Title Center ---------- */
    .center-title {
        text-align: center !important;
        width: 100%;
        display: block;
        margin: auto;
    }

    /* ---------- Buttons ---------- */
    div.stButton > button {
        width: 500px;         
        height: 70px;
        font-size: 20px;
        font-weight: 600;
        text-align: center;
        border-radius: 15px;
        margin: 15px;
    }

    /* Center the 4 buttons in a grid */
    .button-container {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 20px;
    }

    /* ---------- Dropdown ---------- */
    div[data-baseweb="select"] {
        height: 45px !important;
        font-size: 18px !important;
    }
    div[data-baseweb="select"] > div {
        height: 45px !important;
        font-size: 18px !important;
    }

    /* ---------- Fix fog after download ---------- */
    [data-testid="stNotification"] {
        opacity: 1 !important;
        backdrop-filter: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------- BUTTON LAYOUT --------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("🎮 Storytelling"):
        if ticker:
            st.switch_page("pages/1_Storytelling.py")
        else:
            st.error("Pick a stock first!")

    if st.button("📑 PPT Generator"):
        if ticker:
            st.switch_page("pages/2_PPT_Generator.py")
        else:
            st.error("Pick a stock first!")

with col2:
    if st.button("🧩 Analogies"):
        if ticker:
            st.switch_page("pages/3_Analogies.py")
        else:
            st.error("Pick a stock first!")

    if st.button("📊 Professional Data & Trends"):
        if ticker:
            st.switch_page("pages/4_Professional_Dashboard.py")
        else:
            st.error("Pick a stock first!")
