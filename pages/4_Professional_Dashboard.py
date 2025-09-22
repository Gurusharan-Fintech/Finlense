import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime

# For PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(page_title="Professional Dashboard", layout="wide")

# --- Use the stock selected from main page ---
if "selected_stock" in st.session_state and st.session_state["selected_stock"]:
    ticker = st.session_state["selected_stock"]
    st.markdown(f"### 📌 Selected Stock: **{ticker}**")
else:
    st.warning("⚠️ Please choose a stock from the home page to view the Professional Dashboard.")
    st.stop()

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
    unsafe_allow_html=True
)

# =============================
# Dashboard Title
# =============================
st.markdown("<h1 style='text-align: center;'>📊 Professional Data & Trends</h1>", unsafe_allow_html=True)

# =============================
# Layout: Period Selection
# =============================
time_range = st.selectbox("Growth Period", ["1mo", "3mo", "6mo", "1y", "5y", "max"], index=3)

# =============================
# Load Data
# =============================
if ticker:
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
            st.write(info.get('longBusinessSummary', 'No company description available.')[:800] + "...")

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
                height=400
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
            metrics_df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"]).dropna()
            if not metrics_df.empty:
                fig2 = px.bar(metrics_df, x="Metric", y="Value", color="Metric", title="Key Ratios")
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

        # --- PDF Export ---
        with colA:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
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

            # ✅ Build PDF properly
            doc.build(elements)
            pdf_data = buffer.getvalue()
            buffer.close()

            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_data,
                file_name=f"{ticker}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )

        # --- Excel Export ---
        with colB:
            excel_buffer = BytesIO()
            hist.to_excel(excel_buffer, index=True)
            excel_data = excel_buffer.getvalue()

            st.download_button(
                label="📂 Download as Excel",
                data=excel_data,
                file_name=f"{ticker}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:
        st.error("No historical data found for this ticker and time range.")
else:
    st.warning("Please enter a valid stock ticker.")
