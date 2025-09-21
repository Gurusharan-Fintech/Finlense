import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd  # Added missing import

st.set_page_config(page_title="Professional Dashboard", layout="wide")

# --- Use the stock selected from main page ---
if "selected_stock" in st.session_state and st.session_state["selected_stock"]:
    stock_symbol = st.session_state["selected_stock"]
    st.success(f"📌 Selected Stock: **{stock_symbol}**")
else:
    st.warning("⚠️ Please choose a stock from the home page to view the Professional Dashboard.")
    st.stop()  # 🚪 stop execution until a stock is selected

# =============================
# Custom CSS for Styling
# =============================
st.markdown(
    """
    <style>
    div.stButton > button {
        width: 300px;          
        height: 60px;
        font-size: 18px;
        font-weight: 600;
        text-align: center;
        border-radius: 12px;
        margin: 10px;
    }
    div[data-baseweb="select"] {
        height: 50px !important;
        font-size: 16px !important;
    }
    div[data-baseweb="select"] > div {
        height: 50px !important;
        font-size: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True)

# =============================
# Dashboard Title
# =============================
st.markdown("<h1 style='text-align: center;'>📊 Professional Data & Trends</h1>", unsafe_allow_html=True)

# =============================
# Layout: Stock + Period
# =============================
col1, col2 = st.columns([2, 1])

with col1:
    if "selected_stock" in st.session_state and st.session_state["selected_stock"]:
        ticker = st.session_state["selected_stock"]  # ✅ use chosen stock
        st.info(f"Using stock from homepage: {ticker}")
    else:
        ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, RELIANCE.NS, TCS.NS):", "")
        if not ticker:
            st.warning("Please choose a stock from the home page or enter one here.")
            st.stop()

with col2:
    # Added missing time_range selection
    time_range = st.selectbox(
        "Select Time Period:",
        options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        index=3  # Default to 1 year
    )

# =============================
# Load Data
# =============================
if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period=time_range)
        
        if not hist.empty:
            # =============================
            # Overview + Growth Chart
            # =============================
            st.markdown("---")
            col_left, col_right = st.columns([1.3, 2])
            
            with col_left:
                st.subheader(f"📌 Overview: {info.get('shortName', ticker)}")
                description = info.get('longBusinessSummary', 'No company description available.')
                if len(description) > 900:
                    description = description[:900] + "..."
                st.markdown(
                    f"<p style='text-align: left; font-size:16px; line-height:1.6;'>{description}</p>",
                    unsafe_allow_html=True
                )

            with col_right:
                st.subheader("📈 Growth Trend")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist["Close"],
                    mode="lines",
                    name="Closing Price",
                    line=dict(color="royalblue", width=2)
                ))
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Price",
                    template="plotly_white",
                    height=450
                )
                st.plotly_chart(fig, use_container_width=True)

            # =============================
            # Key Metrics + Volume
            # =============================
            st.markdown("---")
            col_left2, col_right2 = st.columns(2)
            
            with col_left2:
                st.subheader("📊 Key Metrics")
                metrics = {
                    "PE Ratio": info.get("trailingPE", None),
                    "Price-to-Book": info.get("priceToBook", None),
                    "Profit Margin": info.get("profitMargins", None),
                    "Return on Equity": info.get("returnOnEquity", None),
                }
                
                # Filter out None values and create DataFrame
                filtered_metrics = {k: v for k, v in metrics.items() if v is not None}
                
                if filtered_metrics:
                    metrics_df = pd.DataFrame(
                        list(filtered_metrics.items()), 
                        columns=["Metric", "Value"]
                    )
                    fig2 = px.bar(
                        metrics_df, 
                        x="Metric", 
                        y="Value", 
                        color="Metric", 
                        title="Key Ratios"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No financial metrics available for this stock.")

            with col_right2:
                st.subheader("📊 Volume Traded")
                fig3 = go.Figure()
                fig3.add_trace(go.Bar(x=hist.index, y=hist["Volume"], marker_color="orange"))
                fig3.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Volume",
                    template="plotly_white",
                    height=400
                )
                st.plotly_chart(fig3, use_container_width=True)

            # =============================
            # Quick Actions
            # =============================
            st.markdown("---")
            st.subheader("⚡ Quick Actions")
            colA, colB = st.columns(2)
            
            with colA:
                if st.button("📑 Download as PDF"):
                    st.info("PDF export coming soon...")
                    
            with colB:
                if st.button("📂 Download as Excel"):
                    try:
                        hist.to_excel("stock_data.xlsx")
                        st.success("Excel file exported as stock_data.xlsx")
                    except Exception as e:
                        st.error(f"Error exporting Excel: {str(e)}")
        else:
            st.error("No historical data found for this ticker and time range.")
            
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")
        
else:
    st.warning("Please enter a valid stock ticker.")
