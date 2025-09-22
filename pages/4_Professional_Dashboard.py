import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
from io import BytesIO
from datetime import datetime
import plotly.io as pio

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
# Layout: Stock + Period  
# =============================
col1, col2 = st.columns([2, 1])

with col1:
    # Get the stock ticker
    if "selected_stock" in st.session_state and st.session_state["selected_stock"]:
        ticker = st.session_state["selected_stock"]
        st.info(f"Using stock from homepage: {ticker}")
    else:
        ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, RELIANCE.NS, TCS.NS):", "")
        if not ticker:
            st.warning("Please choose a stock from the home page or enter one here.")
            st.stop()

with col2:
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
                        title="Key Ratios"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.info("No financial metrics available for this stock.")

            with col_right2:
                st.subheader("📊 Volume Traded")
                fig3 = go.Figure()
                fig3.add_trace(go.Bar(
                    x=hist.index, 
                    y=hist["Volume"], 
                    marker_color="orange"
                ))
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
                    try:
                        # Create PDF content
                        company_name = info.get('shortName', ticker)
                        current_price = hist["Close"].iloc[-1] if not hist.empty else 0
                        price_change = ((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0] * 100) if len(hist) > 1 else 0
                        
                        # Create a simple HTML report
                        html_content = f"""
                        <html>
                        <head>
                            <title>{ticker} Stock Report</title>
                            <style>
                                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                                .header {{ text-align: center; color: #1f77b4; }}
                                .metric {{ background-color: #f0f2f6; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                                .section {{ margin: 20px 0; }}
                            </style>
                        </head>
                        <body>
                            <h1 class="header">📊 {company_name} Stock Report</h1>
                            <p><strong>Report Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                            <p><strong>Stock Symbol:</strong> {ticker}</p>
                            <p><strong>Time Period:</strong> {time_range}</p>
                            
                            <div class="section">
                                <h2>📈 Key Metrics</h2>
                                <div class="metric"><strong>Current Price:</strong> ${current_price:.2f}</div>
                                <div class="metric"><strong>Price Change ({time_range}):</strong> {price_change:+.2f}%</div>
                                <div class="metric"><strong>Highest Price:</strong> ${hist["High"].max():.2f}</div>
                                <div class="metric"><strong>Lowest Price:</strong> ${hist["Low"].min():.2f}</div>
                                <div class="metric"><strong>Average Volume:</strong> {hist["Volume"].mean():,.0f}</div>
                            </div>
                            
                            <div class="section">
                                <h2>📋 Company Information</h2>
                                <p><strong>Sector:</strong> {info.get('sector', 'N/A')}</p>
                                <p><strong>Industry:</strong> {info.get('industry', 'N/A')}</p>
                                <p><strong>Market Cap:</strong> ${info.get('marketCap', 0)/1e9:.1f}B</p>
                                <p><strong>P/E Ratio:</strong> {info.get('trailingPE', 'N/A')}</p>
                            </div>
                            
                            <div class="section">
                                <h2>📊 Recent Price Data (Last 10 Days)</h2>
                                <table border="1" style="border-collapse: collapse; width: 100%;">
                                    <tr style="background-color: #1f77b4; color: white;">
                                        <th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th><th>Volume</th>
                                    </tr>
                        """
                        
                        # Add last 10 days of data
                        for idx, (date, row) in enumerate(hist.tail(10).iterrows()):
                            html_content += f"""
                                    <tr>
                                        <td>{date.strftime("%Y-%m-%d")}</td>
                                        <td>${row['Open']:.2f}</td>
                                        <td>${row['High']:.2f}</td>
                                        <td>${row['Low']:.2f}</td>
                                        <td>${row['Close']:.2f}</td>
                                        <td>{row['Volume']:,.0f}</td>
                                    </tr>
                            """
                        
                        html_content += """
                                </table>
                            </div>
                            
                            <div class="section">
                                <p><em>Report generated by FinLens AI Dashboard</em></p>
                            </div>
                        </body>
                        </html>
                        """
                        
                        # Convert HTML to bytes for download
                        html_bytes = html_content.encode('utf-8')
                        
                        # Create download button
                        st.download_button(
                            label="📄 Download HTML Report",
                            data=html_bytes,
                            file_name=f"{ticker}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                            mime="text/html"
                        )
                        
                        st.success("✅ PDF/HTML report ready for download!")
                        st.info("💡 Open the downloaded HTML file in your browser, then print/save as PDF")
                        
                    except Exception as e:
                        st.error(f"❌ Error creating PDF report: {str(e)}")
                    
            with colB:
                if st.button("📂 Download as Excel"):
                    try:
                        # Create Excel file with multiple sheets
                        buffer = BytesIO()
                        
                        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                            # Sheet 1: Historical Data
                            hist_export = hist.copy()
                            hist_export.index.name = 'Date'
                            hist_export.to_excel(writer, sheet_name='Historical_Data')
                            
                            # Sheet 2: Summary Statistics
                            summary_stats = pd.DataFrame({
                                'Metric': ['Current Price', 'Highest Price', 'Lowest Price', 'Average Price', 
                                          'Total Volume', 'Average Volume', 'Price Change (%)', 'Volatility (%)'],
                                'Value': [
                                    f"${hist['Close'].iloc[-1]:.2f}",
                                    f"${hist['High'].max():.2f}",
                                    f"${hist['Low'].min():.2f}",
                                    f"${hist['Close'].mean():.2f}",
                                    f"{hist['Volume'].sum():,.0f}",
                                    f"{hist['Volume'].mean():,.0f}",
                                    f"{((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100):+.2f}%",
                                    f"{(hist['Close'].pct_change().std() * 100):.2f}%"
                                ]
                            })
                            summary_stats.to_excel(writer, sheet_name='Summary_Stats', index=False)
                            
                            # Sheet 3: Company Info
                            company_info = pd.DataFrame({
                                'Attribute': ['Company Name', 'Sector', 'Industry', 'Market Cap', 'P/E Ratio', 
                                            'Price to Book', 'Profit Margin', 'Report Generated'],
                                'Value': [
                                    info.get('shortName', ticker),
                                    info.get('sector', 'N/A'),
                                    info.get('industry', 'N/A'),
                                    f"${info.get('marketCap', 0)/1e9:.1f}B" if info.get('marketCap') else 'N/A',
                                    info.get('trailingPE', 'N/A'),
                                    info.get('priceToBook', 'N/A'),
                                    f"{info.get('profitMargins', 0)*100:.2f}%" if info.get('profitMargins') else 'N/A',
                                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                ]
                            })
                            company_info.to_excel(writer, sheet_name='Company_Info', index=False)
                        
                        # Create download button
                        excel_data = buffer.getvalue()
                        
                        st.download_button(
                            label="📊 Download Excel File",
                            data=excel_data,
                            file_name=f"{ticker}_data_{time_range}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                        st.success("✅ Excel file ready for download!")
                        st.info("📋 Excel file contains 3 sheets: Historical Data, Summary Stats, and Company Info")
                        
                    except Exception as e:
                        st.error(f"❌ Error creating Excel file: {str(e)}")
                        st.info("💡 Make sure you have the required packages installed")
                        
        else:
            st.error("No historical data found for this ticker and time range.")
            
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")
        
else:
    st.warning("Please enter a valid stock ticker.")
