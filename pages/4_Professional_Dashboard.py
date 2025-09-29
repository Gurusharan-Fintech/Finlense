import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from io import BytesIO
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import subprocess

# -------------------- DATA FETCH --------------------
def load_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d")
        if df.empty:
            return pd.DataFrame()
        df.reset_index(inplace=True)
        return df
    except Exception:
        return pd.DataFrame()

# -------------------- PLOTS --------------------
def price_chart(df, ticker):
    fig = go.Figure()

    # OHLC chart
    fig.add_trace(go.Candlestick(
        x=df['Date'], open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'], name="OHLC"
    ))

    # 200-day MA
    if len(df) > 200:
        df['MA200'] = df['Close'].rolling(200).mean()
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['MA200'], mode='lines',
            name="200 MA", line=dict(color="blue")
        ))

    fig.update_layout(title=f"{ticker} Price Movement", xaxis_title="Date", yaxis_title="Price")
    return fig

def volume_chart(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], name="Volume", marker_color="orange"))
    fig.update_layout(title=f"{ticker} Volume Trends", xaxis_title="Date", yaxis_title="Volume")
    return fig

# -------------------- EXPORTS --------------------
def create_excel(df, ticker):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Stock Data")
    return buffer

def create_pdf(ticker, df, ai_text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Stock Report: {ticker}", styles["Title"]))
    story.append(Spacer(1, 12))

    # Safe stats
    try:
        latest_close = float(df['Close'].iloc[-1])
    except Exception:
        latest_close = "N/A"

    try:
        avg_volume = float(df['Volume'].mean())
    except Exception:
        avg_volume = "N/A"

    stats = [
        ["Metric", "Value"],
        ["Latest Close", latest_close],
        ["Average Volume", avg_volume],
    ]

    table = Table(stats)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 1, colors.black)
    ]))

    story.append(table)
    story.append(Spacer(1, 24))
    story.append(Paragraph("AI Summary:", styles["Heading2"]))
    story.append(Paragraph(ai_text, styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------- AI SUMMARY --------------------
def get_ai_summary(ticker, df):
    try:
        subprocess.run(["ollama", "--version"], check=True, capture_output=True)
        prompt = f"Summarize stock performance for {ticker} in 3-4 sentences."
        result = subprocess.run(["ollama", "run", "llama3"], input=prompt.encode(), capture_output=True)
        return result.stdout.decode().strip()
    except Exception:
        return "AI summary not available (Ollama not installed)."

# -------------------- MAIN APP --------------------
def main():
    st.title("📈 Professional Dashboard")

    if "selected_ticker" not in st.session_state:
        st.warning("⚠️ Please select a stock ticker on the homepage.")
        return

    ticker = st.session_state["selected_ticker"]
    st.subheader(f"Showing analysis for: {ticker}")

    df = load_data(ticker)

    if df.empty:
        st.error("No data found for this ticker. Try another one.")
        return

    # Charts
    st.plotly_chart(price_chart(df, ticker), use_container_width=True)
    st.plotly_chart(volume_chart(df, ticker), use_container_width=True)

    # AI Summary
    ai_text = get_ai_summary(ticker, df)
    st.subheader("🤖 AI Summary")
    st.write(ai_text)

    # Downloads
    st.subheader("📥 Export Data")

    excel_buffer = create_excel(df, ticker)
    st.download_button("Download Excel", data=excel_buffer, file_name=f"{ticker}_data.xlsx")

    pdf_buffer = create_pdf(ticker, df, ai_text)
    st.download_button("Download PDF", data=pdf_buffer, file_name=f"{ticker}_report.pdf")

if __name__ == "__main__":
    main()
