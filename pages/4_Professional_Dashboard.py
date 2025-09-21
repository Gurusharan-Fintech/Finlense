import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# =============================
# Custom CSS for Styling
# =============================
st.markdown(
    """
    <style>
    div.stButton > button {
        width: 500px;  
        height: 70px;
        font-size: 20px;
        font-weight: 600;
        text-align: center;
        border-radius: 15px;
        margin: 15px;
    }

    .button-container {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 20px;
    }

    div[data-baseweb="select"] {
        height: 55px !important;
        font-size: 18px !important;
    }

    div[data-baseweb="select"] > div {
        height: 55px !important;
        font-size: 18px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =============================
# Dashboard Title
# =============================
st.title("📊 Professional Data & Trends")

# =============================
# Stock Input
# =============================
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, RELIANCE.NS, TCS.NS):", "AAPL")

if ticker:
    stock = yf.Ticker(ticker)

    # Basic stock info
    info = stock.info

    st.subheader(f"📌 Overview: {info.get('shortName', ticker)}")
    st.write(
        f"{info.get('longBusinessSummary', 'No company description available.')[:500]}..."
    )

    # =============================
    # Chart 1: Growth Trend
    # =============================
    st.subheader("📈 Price Growth Over Time")

    time_range = st.selectbox("Select Time Range", ["1mo", "3mo", "6mo", "1y", "5y", "max"])

    hist = stock.history(period=time_range)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(hist.index, hist["Close"], label="Closing Price", color="blue")
    ax.set_title(f"{ticker} Stock Price ({time_range})")
    ax.set_ylabel("Price (USD)")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    # =============================
    # Chart 2: Key Metrics
    # =============================
    st.subheader("📊 Key Financial Metrics")

    metrics = {
        "PE Ratio": info.get("trailingPE", None),
        "Price-to-Book": info.get("priceToBook", None),
        "Profit Margin": info.get("profitMargins", None),
        "Return on Equity": info.get("returnOnEquity", None),
    }

    metrics_df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"]).dropna()

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.bar(metrics_df["Metric"], metrics_df["Value"], color="green")
    ax2.set_title("Key Financial Ratios")
    ax2.set_ylabel("Value")
    st.pyplot(fig2)

    # =============================
    # Action Buttons
    # =============================
    st.subheader("⚡ Quick Actions")
    st.markdown('<div class="button-container">', unsafe_allow_html=True)

    if st.button("📑 Download Report"):
        st.write("Report download feature coming soon...")

    if st.button("📂 Export Data to CSV"):
        metrics_df.to_csv("metrics.csv", index=False)
        st.success("Metrics exported as metrics.csv")

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning("Please enter a valid stock ticker.")
