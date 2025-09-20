import streamlit as st
import yfinance as yf

# -------------------- APP CONFIG --------------------
st.set_page_config(page_title="FinLens AI", page_icon="📈", layout="wide")

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

st.session_state["selected_ticker"] = ticker  # save stock for all pages

# -------------------- NAVIGATION BUTTONS --------------------
st.markdown("### Choose a mode")

col1, col2 = st.columns(2)

with col1:
  if st.button("🎮 Storytelling", use_container_width=True):
     st.switch_page("pages/1_Storytelling.py")

  if st.button("📑 PPT Generator", use_container_width=True):
     st.switch_page("pages/2_PPT_Generator.py")
      
with col2:
 if st.button("🧩 Analogies", use_container_width=True):
    st.switch_page("pages/3_Analogies.py")

 if st.button("📊 Professional Data & Trends", use_container_width=True):
    st.switch_page("pages/4_Professional_Dashboard.py")

