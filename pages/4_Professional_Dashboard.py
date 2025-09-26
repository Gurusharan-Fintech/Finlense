import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from datetime import datetime

# PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

# Excel
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference

# AI fallback
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


# ==============================
# Function: Fetch stock data
# ==============================
def get_stock_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    df.index = df.index.tz_localize(None)  # remove timezone
    return df


# ==============================
# Function: AI Analysis
# ==============================
def generate_ai_analysis(ticker, df):
    prompt = f"""
    Analyze the stock {ticker} using the following data:
    - Latest Close Price: {df['Close'][-1]:.2f}
    - 7-day average: {df['Close'][-7:].mean():.2f}
    - 30-day average: {df['Close'][-30:].mean():.2f}
    - Max price in given range: {df['Close'].max():.2f}
    - Min price in given range: {df['Close'].min():.2f}

    Provide:
    1. A professional analysis of the stock performance.
    2. Prediction (bullish, bearish, or neutral trend).
    3. Key reasons behind this prediction.
    4. Risks and opportunities for investors.
    """

    if OLLAMA_AVAILABLE:
        try:
            response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
            return response["message"]["content"]
        except Exception as e:
            return f"⚠️ Ollama error: {e}\n\nFallback analysis: Based on the given metrics, the stock shows stable performance."
    else:
        return f"""
        (Fallback - AI model not available)

        Stock {ticker} shows a latest close price of {df['Close'][-1]:.2f}. 
        The short-term average ({df['Close'][-7:].mean():.2f}) compared to the 30-day average 
        ({df['Close'][-30:].mean():.2f}) indicates {'upward momentum' if df['Close'][-7:].mean() > df['Close'][-30:].mean() else 'sideways or downward pressure'}.

        Risks: market volatility, macroeconomic factors.  
        Opportunities: momentum trading, medium-term hold.
        """


# ==============================
# Function: Generate PDF
# ==============================
def create_pdf(ticker, df, ai_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>Stock Analysis Report - {ticker}</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>AI Analysis:</b>", styles["Heading2"]))
    elements.append(Paragraph(ai_text, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Generate chart
    fig, ax = plt.subplots(figsize=(6, 3))
    df["Close"].plot(ax=ax, title=f"{ticker} Closing Prices")
    chart_path = f"{ticker}_chart.png"
    fig.savefig(chart_path)
    plt.close(fig)

    elements.append(Image(chart_path, width=400, height=200))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>Summary Metrics:</b>", styles["Heading2"]))
    elements.append(Paragraph(f"Latest Close: {df['Close'][-1]:.2f}", styles["Normal"]))
    elements.append(Paragraph(f"7-day Avg: {df['Close'][-7:].mean():.2f}", styles["Normal"]))
    elements.append(Paragraph(f"30-day Avg: {df['Close'][-30:].mean():.2f}", styles["Normal"]))
    elements.append(Paragraph(f"Max: {df['Close'].max():.2f}", styles["Normal"]))
    elements.append(Paragraph(f"Min: {df['Close'].min():.2f}", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer


# ==============================
# Function: Generate Excel
# ==============================
def create_excel(ticker, df, ai_text):
    output = BytesIO()
    wb = Workbook()
    ws_data = wb.active
    ws_data.title = "Stock Data"

    # Write data
    ws_data.append(["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"])
    for idx, row in df.iterrows():
        ws_data.append([idx.strftime("%Y-%m-%d")] + list(row.values))

    # Add chart
    chart = LineChart()
    chart.title = f"{ticker} Closing Prices"
    data = Reference(ws_data, min_col=5, min_row=1, max_row=len(df) + 1)
    chart.add_data(data, titles_from_data=True)
    ws_data.add_chart(chart, "I5")

    # AI Sheet
    ws_ai = wb.create_sheet("AI Analysis")
    ws_ai["A1"] = f"AI Analysis for {ticker}"
    ws_ai["A2"] = ai_text

    wb.save(output)
    output.seek(0)
    return output


# ==============================
# Streamlit Dashboard
# ==============================
def main():
    st.set_page_config(page_title="Professional Stock Dashboard", layout="wide")

    # Custom CSS
    st.markdown(
        """
        <style>
        .stApp {
            background: #f8fafc;
            font-family: 'Segoe UI', sans-serif;
        }
        h1, h2, h3 {
            color: #1e3a8a;
        }
        .block-container {
            padding: 2rem 3rem;
        }
        .stDownloadButton>button, .stButton>button {
            background: #1e3a8a;
            color: white;
            border-radius: 10px;
            padding: 0.6rem 1rem;
            border: none;
            font-weight: 600;
        }
        .stDownloadButton>button:hover, .stButton>button:hover {
            background: #2563eb;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --- Use the stock selected from main page ---
    if "selected_stock" in st.session_state and st.session_state["selected_stock"]:
        ticker = st.session_state["selected_stock"]
        st.success(f"📌 Selected Stock: **{ticker}**")
    else:
        st.warning("⚠️ Please choose a stock from the home page to view the Professional Dashboard.")
        st.stop()

    # Load data
    start_date = datetime(2023, 1, 1)
    end_date = datetime.today()
    df = get_stock_data(ticker, start_date, end_date)

    # AI Analysis
    st.subheader("🤖 AI-Powered Stock Analysis")
    ai_text = generate_ai_analysis(ticker, df)
    st.write(ai_text)

    # Charts
    st.subheader("📈 Stock Price Charts")
    col1, col2 = st.columns(2)

    with col1:
        fig_candle = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )])
        fig_candle.update_layout(title=f"{ticker} Candlestick Chart", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_candle, use_container_width=True)

    with col2:
        df["MA30"] = df["Close"].rolling(30).mean()
        fig_ma = px.line(df, x=df.index, y=["Close", "MA30"], title=f"{ticker} - Close vs 30-day MA")
        st.plotly_chart(fig_ma, use_container_width=True)

    # Downloads
    st.subheader("📥 Download Reports")
    col_pdf, col_excel = st.columns(2)

    pdf_buffer = create_pdf(ticker, df, ai_text)
    col_pdf.download_button("Download PDF Report", data=pdf_buffer, file_name=f"{ticker}_report.pdf", mime="application/pdf")

    excel_buffer = create_excel(ticker, df, ai_text)
    col_excel.download_button("Download Excel Report", data=excel_buffer, file_name=f"{ticker}_report.xlsx", mime="application/vnd.ms-excel")

    # Note for committee
    st.info("⚠️ To enable full AI analysis, please install [Ollama](https://ollama.ai) and run: `ollama pull mistral`.")


if __name__ == "__main__":
    main()
