import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import subprocess

st.set_page_config(page_title="📊 Professional Dashboard", layout="wide")

# ---------------- CSS ----------------
st.markdown(
    """
    <style>
    .main {
        background-color: #f9f9f9;
        padding: 2rem 3rem;
    }
    h1, h2, h3, h4 {
        font-family: 'Segoe UI', sans-serif;
        font-weight: 600;
        color: #222;
    }
    .stButton>button {
        width: 220px;
        height: 60px;
        font-size: 18px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- AI Analysis ----------------
def generate_ai_analysis(ticker, df):
    if df.empty:
        return "No data available for AI analysis."

    prompt = f"""
    Provide a professional financial analysis for stock: {ticker}.
    Include:
    - Market performance
    - Key trends from historical data
    - Risks and opportunities
    - A prediction with reasoning.
    Data sample: {df.tail(5).to_string()}
    """

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return f"⚠️ Ollama error: {result.stderr}"
        return result.stdout.strip()
    except FileNotFoundError:
        return "⚠️ AI analysis unavailable (Ollama not installed). Please install it from https://ollama.ai/."
    except Exception as e:
        return f"⚠️ AI analysis failed: {e}"

# ---------------- PDF Export ----------------
def create_pdf(ticker, df, ai_text):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, f"Stock Report: {ticker}")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 100, "AI Analysis Summary:")
    text = pdf.beginText(50, height - 120)
    text.setFont("Helvetica", 10)
    for line in ai_text.split("\n"):
        text.textLine(line)
    pdf.drawText(text)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer

# ---------------- Excel Export ----------------
def create_excel(ticker, df, ai_text):
    buffer = io.BytesIO()
    df_reset = df.copy().reset_index()

    # Flatten MultiIndex if exists
    if isinstance(df_reset.columns, pd.MultiIndex):
        df_reset.columns = ["_".join([str(c) for c in col if c]) for col in df_reset.columns]

    if "Date" in df_reset.columns:
        df_reset["Date"] = pd.to_datetime(df_reset["Date"]).dt.tz_localize(None)

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_reset.to_excel(writer, sheet_name="Stock Data", index=False)

        summary_df = pd.DataFrame({"AI Analysis": ai_text.split("\n")})
        summary_df.to_excel(writer, sheet_name="AI Summary", index=False)

    buffer.seek(0)
    return buffer

# ---------------- Plotting ----------------
def plot_stock_chart(df, ticker):
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Candlestick"
            )
        ]
    )
    fig.update_layout(
        title=f"{ticker} - Price Trends",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        height=500
    )
    return fig

# ---------------- MAIN ----------------
def main():
    st.title("📊 Professional Data & Trends")

    if "selected_stock" in st.session_state:
        ticker = st.session_state["selected_stock"]
    else:
        st.info("🔎 Please choose a stock in the main page to continue.")
        return

    df = yf.download(ticker, period="6mo", interval="1d")

    if df.empty:
        st.warning("No data available for this stock.")
        return

    st.subheader("🤖 AI Stock Analysis")
    ai_text = generate_ai_analysis(ticker, df)
    st.write(ai_text)

    st.subheader("📈 Price Movement")
    st.plotly_chart(plot_stock_chart(df, ticker), use_container_width=True)

    st.subheader("⚡ Quick Actions")
    col1, col2 = st.columns(2)

    with col1:
        pdf_buffer = create_pdf(ticker, df, ai_text)
        st.download_button(
            "📥 Download Detailed PDF",
            data=pdf_buffer,
            file_name=f"{ticker}_report.pdf",
            mime="application/pdf",
        )

    with col2:
        excel_buffer = create_excel(ticker, df, ai_text)
        st.download_button(
            "📊 Download Excel Report",
            data=excel_buffer,
            file_name=f"{ticker}_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()

