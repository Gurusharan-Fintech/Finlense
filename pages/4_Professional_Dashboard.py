import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import subprocess

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
        height: 40px !important;
        font-size: 16px !important;
    }
    div[data-baseweb="select"] > div {
        height: 40px !important;
        font-size: 16px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =============================
# Dashboard Title
# =============================
st.markdown("<h1 style='text-align: center;'>📊 Professional Data & AI Analysis</h1>", unsafe_allow_html=True)

# =============================
# Layout: Stock + Period
# =============================
col1, col2 = st.columns([2, 1])

with col1:
    ticker = stock_symbol  # use the stock passed from main page

with col2:
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
            st.write(info.get('longBusinessSummary', 'No company description available.')[:700] + "...")

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
        # AI Analysis (Mistral via Ollama)
        # =============================
        st.markdown("---")
        st.subheader("🤖 AI-Powered Analysis & Prediction")

        user_prompt = f"""
        Analyze the stock {ticker} using the following metrics:
        PE Ratio: {info.get("trailingPE", "N/A")},
        Price-to-Book: {info.get("priceToBook", "N/A")},
        Profit Margin: {info.get("profitMargins", "N/A")},
        Return on Equity: {info.get("returnOnEquity", "N/A")}.
        Provide a detailed professional analysis including:
        - Current performance overview
        - Possible growth potential
        - Risks and challenges
        - A prediction of near-term trend
        Keep it concise but insightful.
        """

        try:
            with st.spinner("🤖 Generating AI analysis..."):
                result = subprocess.run(
                    ["ollama", "run", "mistral"],
                    input=user_prompt,
                    capture_output=True,
                    text=True  # ✅ ensures input/output are treated as strings
                )

            if result.returncode == 0:
                ai_response = result.stdout.strip()
                if ai_response:
                    st.write(ai_response)
                else:
                    st.warning("⚠️ AI model returned no response. Make sure Mistral is installed in Ollama.")
            else:
                st.warning("⚠️ Ollama not found. Please install Ollama & Mistral locally to enable AI predictions.")

        except FileNotFoundError:
            st.error("⚠️ Ollama is not installed. Please download it from: https://ollama.ai")

        except Exception as e:
            st.warning(f"⚠️ AI analysis could not be generated. Error: {e}")

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

        with colA:
            if st.button("📑 Download as PDF"):
                pdf_buffer = BytesIO()
                c = canvas.Canvas(pdf_buffer, pagesize=letter)
                c.setFont("Helvetica", 12)
                c.drawString(100, 750, f"Stock Report: {ticker}")
                c.drawString(100, 730, f"Period: {time_range}")
                c.drawString(100, 710, f"PE Ratio: {info.get('trailingPE', 'N/A')}")
                c.drawString(100, 690, f"Price-to-Book: {info.get('priceToBook', 'N/A')}")
                c.drawString(100, 670, f"Profit Margin: {info.get('profitMargins', 'N/A')}")
                c.drawString(100, 650, f"Return on Equity: {info.get('returnOnEquity', 'N/A')}")
                c.save()
                pdf_buffer.seek(0)
                st.download_button(
                    "⬇️ Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"{ticker}_report.pdf",
                    mime="application/pdf"
                )

        with colB:
            if st.button("📂 Download as Excel"):
                excel_buffer = BytesIO()
                hist.index = hist.index.tz_localize(None)  # remove timezone for Excel compatibility
                hist.to_excel(excel_buffer, index=True)
                excel_buffer.seek(0)
                st.download_button(
                    "⬇️ Download Excel Data",
                    data=excel_buffer,
                    file_name=f"{ticker}_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    else:
        st.error("No historical data found for this ticker and time range.")
else:
    st.warning("Please enter a valid stock ticker.")
