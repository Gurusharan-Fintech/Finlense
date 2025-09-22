import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

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
    unsafe_allow_html=True,
)

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
        ticker = st.session_state["selected_stock"]

        # ✅ Read-only dropdown
        st.selectbox(
            "Chosen Stock (from homepage):",
            options=[ticker],
            index=0,
            disabled=True
        )
    else:
        st.warning("⚠️ Please choose a stock from the home page first.")
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
                filtered_metrics = {k: v for k, v in metrics.items() if v is not None}

                if filtered_metrics:
                    metrics_df = pd.DataFrame(list(filtered_metrics.items()), columns=["Metric", "Value"])
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

            # --- PDF Download ---
            with colA:
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer)
                styles = getSampleStyleSheet()
                elements = []

                company_name = info.get('shortName', ticker)
                current_price = hist["Close"].iloc[-1] if not hist.empty else 0
                price_change = ((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0] * 100) if len(hist) > 1 else 0

                elements.append(Paragraph(f"<b>{company_name} Stock Report</b>", styles['Title']))
                elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
                elements.append(Spacer(1, 12))

                data = [
                    ["Stock Symbol", ticker],
                    ["Time Period", time_range],
                    ["Current Price", f"${current_price:.2f}"],
                    [f"Price Change ({time_range})", f"{price_change:+.2f}%"],
                    ["Highest Price", f"${hist['High'].max():.2f}"],
                    ["Lowest Price", f"${hist['Low'].min():.2f}"],
                    ["Average Volume", f"{hist['Volume'].mean():,.0f}"],
                ]
                table = Table(data, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)

                doc.build(elements)
                pdf_data = buffer.getvalue()

                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_data,
                    file_name=f"{ticker}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )

            # --- Excel Download ---
            with colB:
                try:
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        # Historical Data
                        hist_export = hist.copy()
                        hist_export.index = hist_export.index.tz_localize(None) if hist_export.index.tz is not None else hist_export.index
                        hist_export.index.name = 'Date'
                        hist_export.to_excel(writer, sheet_name='Historical_Data')

                        # Summary Stats
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

                        # Company Info
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

                    excel_data = buffer.getvalue()
                    st.download_button(
                        label="📊 Download Excel File",
                        data=excel_data,
                        file_name=f"{ticker}_data_{time_range}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"❌ Error creating Excel file: {str(e)}")

        else:
            st.error("No historical data found for this ticker and time range.")

    except Exception as e:
        st.error(f"Error loading data for {ticker}: {str(e)}")

else:
    st.warning("Please enter a valid stock ticker.")
