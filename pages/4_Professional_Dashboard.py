import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Professional Dashboard", layout="wide")

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
# Get Stock from Session State
# =============================
# Debug info - remove these lines once working
st.write(f"Debug: All session state: {dict(st.session_state)}")

# Get the stock ticker
ticker = None
if "selected_stock" in st.session_state and st.session_state["selected_stock"]:
    ticker = st.session_state["selected_stock"]
    st.success(f"📌 Using Stock from Homepage: **{ticker}**")
else:
    st.warning("⚠️ No stock selected from homepage")
    ticker = st.text_input("Enter Stock Ticker manually:", "")
    if not ticker:
        st.info("Please go back to homepage and select a stock, or enter one above.")
        st.stop()

# Time period selection
time_range = st.selectbox(
    "📅 Select Time Period:",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=3  # Default to 1 year
)

st.write(f"Debug: Using ticker = {ticker}, time_range = {time_range}")

# =============================
# Load Data
# =============================
if ticker:
    try:
        st.info(f"Loading data for {ticker}...")
        
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period=time_range)
        
        st.write(f"Debug: Got {len(hist)} data points")
        
        if not hist.empty:
            # =============================
            # Overview + Growth Chart
            # =============================
            st.markdown("---")
            col_left, col_right = st.columns([1.3, 2])
            
            with col_left:
                company_name = info.get('shortName', info.get('longName', ticker))
                st.subheader(f"📌 Overview: {company_name}")
                
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
                    title=f"{ticker} Price Trend",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
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
                    "PE Ratio": info.get("trailingPE"),
                    "Price-to-Book": info.get("priceToBook"),
                    "Profit Margin": info.get("profitMargins"),
                    "Return on Equity": info.get("returnOnEquity"),
                }
                
                # Filter out None values
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
                        title=f"Key Financial Ratios - {ticker}"
                    )
                    fig2.update_layout(showlegend=False)
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No financial metrics available for this stock.")

            with col_right2:
                st.subheader("📊 Volume Traded")
                fig3 = go.Figure()
                fig3.add_trace(go.Bar(
                    x=hist.index, 
                    y=hist["Volume"], 
                    marker_color="orange",
                    name="Volume"
                ))
                fig3.update_layout(
                    title=f"{ticker} Trading Volume",
                    xaxis_title="Date",
                    yaxis_title="Volume",
                    template="plotly_white",
                    height=400
                )
                st.plotly_chart(fig3, use_container_width=True)

            # =============================
            # Additional Stock Info
            # =============================
            st.markdown("---")
            st.subheader("📋 Stock Information")
            
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                current_price = hist["Close"].iloc[-1] if not hist.empty else "N/A"
                st.metric("Current Price", f"${current_price:.2f}" if current_price != "N/A" else "N/A")
                
            with col_info2:
                market_cap = info.get("marketCap")
                if market_cap:
                    st.metric("Market Cap", f"${market_cap/1e9:.1f}B")
                else:
                    st.metric("Market Cap", "N/A")
                    
            with col_info3:
                sector = info.get("sector", "N/A")
                st.metric("Sector", sector)

            # =============================
            # Quick Actions
            # =============================
            st.markdown("---")
            st.subheader("⚡ Quick Actions")
            colA, colB = st.columns(2)
            
            with colA:
                if st.button("📑 Download as PDF"):
                    st.info("PDF export feature coming soon...")
                    
            with colB:
                if st.button("📂 Download as Excel"):
                    try:
                        filename = f"{ticker}_data_{time_range}.xlsx"
                        hist.to_excel(filename)
                        st.success(f"✅ Excel file exported as {filename}")
                    except Exception as e:
                        st.error(f"❌ Error exporting Excel: {str(e)}")
                        
        else:
            st.error(f"❌ No historical data found for {ticker} in the {time_range} period.")
            st.info("Try a different time period or check if the ticker symbol is correct.")
            
    except Exception as e:
        st.error(f"❌ Error loading data for {ticker}: {str(e)}")
        st.info("Please check if the ticker symbol is correct and try again.")
        
else:
    st.warning("Please select a stock to continue.")
