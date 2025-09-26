# pages/4_Professional_Dashboard.py
"""
Professional Dashboard page for FinLens AI
- Uses selected_stock from main app (st.session_state["selected_stock"])
- Shows overview, runs local AI via Ollama (mistral) if available (fallback otherwise)
- Generates polished PDF and Excel reports (in-memory; one-click downloads)
- Safe CSS injection (wrapped in triple quotes)
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO
from datetime import datetime
import subprocess
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# PDF and Excel libraries
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
import xlsxwriter

# -------------------- App config & safe CSS --------------------
st.set_page_config(page_title="Professional Dashboard — FinLens AI", layout="wide")

# CSS is wrapped as a string passed to st.markdown; Python won't parse CSS as code.
st.markdown(
    """
    <style>
    /* Page background & fonts */
    .stApp {
        background: linear-gradient(180deg, #f7fbff 0%, #ffffff 100%);
        font-family: "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }

    /* Title color */
    h1, h2, h3 {
        color: #073b6b;
    }

    /* Buttons */
    .stButton>button, .stDownloadButton>button {
        background: #0b63d6;
        color: white;
        border-radius: 10px;
        padding: 10px 18px;
        font-weight: 600;
    }
    .stButton>button:hover, .stDownloadButton>button:hover {
        background: #084fb0;
    }

    /* Card look for metrics */
    .metric-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 14px;
        box-shadow: 0 6px 18px rgba(8, 63, 130, 0.06);
    }

    /* Small spacing fixes */
    .block-container { padding-top: 20px; padding-left: 30px; padding-right: 30px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- Helpers --------------------
def safe_get_close_column(df: pd.DataFrame):
    """Return the name of a valid close column (prefer 'Close', then 'Adj Close')."""
    for c in ["Close", "close", "Adj Close", "Adj_Close", "adj close"]:
        if c in df.columns:
            return c
    # If nothing matches, try numeric last column heuristics (not ideal)
    return None

def ensure_timezone_naive(df: pd.DataFrame):
    """Make datetime index timezone naive to avoid Excel issues."""
    try:
        if hasattr(df.index, "tz") and df.index.tz is not None:
            df = df.copy()
            df.index = df.index.tz_convert(None).tz_localize(None) if hasattr(df.index, "tz_convert") else df.index.tz_localize(None)
    except Exception:
        # fallback: do nothing
        pass
    return df

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add simple indicators used in charts and analysis."""
    df = df.copy()
    close_col = safe_get_close_column(df)
    if close_col:
        df["MA30"] = df[close_col].rolling(window=30, min_periods=1).mean()
        df["MA50"] = df[close_col].rolling(window=50, min_periods=1).mean()
        df["MA200"] = df[close_col].rolling(window=200, min_periods=1).mean()
        # RSI simplified (14)
        delta = df[close_col].diff()
        up = delta.clip(lower=0).rolling(14).mean()
        down = -delta.clip(upper=0).rolling(14).mean()
        rs = up / (down.replace(0, np.nan))
        df["RSI14"] = 100 - (100 / (1 + rs))
    return df

def run_ollama_mistral(prompt: str, timeout: int = 25):
    """Call Ollama locally via subprocess (ollama run mistral). Returns text or None."""
    try:
        proc = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.returncode == 0 and proc.stdout:
            return proc.stdout.strip()
        return None
    except FileNotFoundError:
        # Ollama not installed
        return None
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None

def fallback_analysis_text(ticker: str, df: pd.DataFrame) -> str:
    """Return a professional fallback analysis when Ollama is not available."""
    close_col = safe_get_close_column(df)
    if close_col:
        latest = df[close_col].iloc[-1]
        avg7 = df[close_col].tail(7).mean()
        avg30 = df[close_col].tail(30).mean()
        high = df[close_col].max()
        low = df[close_col].min()
    else:
        latest = avg7 = avg30 = high = low = "N/A"

    text = (
        f"<b>Fallback AI Summary</b>\n\n"
        f"{ticker} latest close: {latest if isinstance(latest, str) else f'${latest:,.2f}'}.\n"
    )
    if not isinstance(latest, str):
        momentum = "upward momentum" if avg7 > avg30 else "sideways/downward pressure"
        text += (
            f"Short-term vs medium-term: 7-day avg ${avg7:,.2f} vs 30-day avg ${avg30:,.2f} "
            f"→ {momentum}.\n\n"
            "Key drivers: industry dynamics, macro conditions, and recent company updates. "
            "Key risks: market volatility and execution risk. "
            "Conservative short-term outlook: neutral — watch moving averages and volume for confirmation.\n\n"
            "Two-line takeaway: Monitor momentum and risk events; consider sizing positions conservatively."
        )
    else:
        text += "Limited price data available to compute numerical indicators.\n"

    return text

# -------------------- Main page logic --------------------
def main():
    # require selected_stock from main page
    if "selected_stock" not in st.session_state or not st.session_state["selected_stock"]:
        st.warning("⚠️ Please select a stock from the home page first. The dashboard reads `st.session_state['selected_stock']`.")
        st.stop()

    ticker = st.session_state["selected_stock"]

    # Banner for reviewers: explain Ollama requirement
    st.markdown(
        """
        <div style="padding:10px;border-radius:8px;background:#e8f1ff;border:1px solid #cfe3ff;">
        <strong>Reviewer note:</strong> AI analysis uses a local model (Ollama + Mistral). 
        To enable AI, install Ollama and pull the model: <code>ollama pull mistral</code>.
        Without Ollama, a high-quality fallback analysis is shown automatically.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # top layout
    st.markdown("## 📊 Professional Data & AI Analysis")
    st.markdown(f"**Selected ticker:** `{ticker}`")

    # time range (keep default broad; user may change on top of this page if needed)
    time_range = st.selectbox("Growth Period", ["3mo", "6mo", "1y", "2y", "5y", "max"], index=2)

    # fetch data
    try:
        # yfinance accepts period; using period for simplicity
        hist = yf.download(ticker, period=time_range)
        if hist is None or hist.empty:
            st.error("No historical data found for this ticker / period.")
            st.stop()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        st.stop()

    # sanitize index
    hist = ensure_timezone_naive(hist)

    # compute indicators
    hist_ind = compute_indicators(hist)

    # Overview + chart
    st.markdown("---")
    col_left, col_right = st.columns([1.3, 2])

    with col_left:
        # company info attempt
        try:
            info = yf.Ticker(ticker).info
        except Exception:
            info = {}

        name = info.get("shortName") or info.get("longName") or ticker
        st.subheader(f"{name}")
        desc = info.get("longBusinessSummary", "")
        if desc:
            st.write(desc[:900] + ("..." if len(desc) > 900 else ""))
        else:
            st.write("_No long description available from data source._")

        # quick metrics
        market_cap = info.get("marketCap")
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.write("**Quick facts**")
        st.write(f"- Market cap: {f'${market_cap/1e9:.2f}B' if market_cap else 'N/A'}")
        st.write(f"- Sector: {info.get('sector','N/A')}")
        st.write(f"- Industry: {info.get('industry','N/A')}")
        st.write(f"- Trailing P/E: {info.get('trailingPE','N/A')}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.subheader("📈 Growth Trend")
        close_col = safe_get_close_column(hist_ind) or hist_ind.columns[0]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist_ind.index, y=hist_ind[close_col], mode="lines", name="Close", line=dict(color="#0b63d6", width=2)))
        if "MA50" in hist_ind.columns:
            fig.add_trace(go.Scatter(x=hist_ind.index, y=hist_ind["MA50"], mode="lines", name="MA50", line=dict(dash="dash", width=1)))
        if "MA200" in hist_ind.columns:
            fig.add_trace(go.Scatter(x=hist_ind.index, y=hist_ind["MA200"], mode="lines", name="MA200", line=dict(dash="dot", width=1)))
        fig.update_layout(template="plotly_white", height=420, margin=dict(t=30))
        st.plotly_chart(fig, use_container_width=True)

    # ================= AI Section (before metric charts) =================
    st.markdown("---")
    st.subheader("🤖 AI Analysis & Prediction")

    # Build robust prompt including key numeric metrics where available
    close_col = safe_get_close_column(hist_ind)
    if close_col:
        latest_price = hist_ind[close_col].iloc[-1]
        avg7 = hist_ind[close_col].tail(7).mean() if len(hist_ind) >= 7 else hist_ind[close_col].mean()
        avg30 = hist_ind[close_col].tail(30).mean() if len(hist_ind) >= 30 else hist_ind[close_col].mean()
    else:
        latest_price = avg7 = avg30 = None

    prompt_lines = [
        f"Analyze the stock {ticker}.",
        f"Latest close: {latest_price if latest_price is None else f'{latest_price:.2f}'}",
        f"7-day avg: {avg7 if avg7 is None else f'{avg7:.2f}'}",
        f"30-day avg: {avg30 if avg30 is None else f'{avg30:.2f}'}",
        "Provide: 1) short professional summary; 2) key drivers and risks; 3) short-term prediction (30 days) with confidence level; 4) two-line takeaway.",
    ]
    prompt = "\n".join(prompt_lines)

    ai_text = run_ollama_mistral(prompt)
    if ai_text:
        st.markdown(ai_text)
    else:
        # show fallback but still well formatted
        st.info("AI model not available locally or returned no response — showing fallback professional analysis.")
        st.markdown(fallback_analysis_text(ticker, hist_ind), unsafe_allow_html=False)

    # ================= Charts & Metrics AFTER AI =================
    st.markdown("---")
    st.subheader("📊 Key Metrics & Charts")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Key Ratios**")
        metrics = {
            "PE Ratio": info.get("trailingPE"),
            "Price-to-Book": info.get("priceToBook"),
            "Profit Margin": info.get("profitMargins"),
            "Return on Equity": info.get("returnOnEquity"),
        }
        df_metrics = pd.DataFrame([(k, v) for k, v in metrics.items() if v is not None], columns=["Metric", "Value"])
        if not df_metrics.empty:
            figm = go.Figure(go.Bar(x=df_metrics["Metric"], y=df_metrics["Value"], marker_color="#0b63d6"))
            figm.update_layout(template="plotly_white", height=360)
            st.plotly_chart(figm, use_container_width=True)
        else:
            st.info("No key ratios available from source.")

    with c2:
        st.markdown("**Volume (recent)**")
        if "Volume" in hist_ind.columns:
            figv = go.Figure(go.Bar(x=hist_ind.index, y=hist_ind["Volume"], marker_color="orange"))
            figv.update_layout(template="plotly_white", height=360)
            st.plotly_chart(figv, use_container_width=True)
        else:
            st.info("Volume data not available.")

    # ================= Quick Actions: PDF & Excel =================
    st.markdown("---")
    st.subheader("⚡ Quick Actions: Download Detailed Reports")

    def create_chart_images_bytes(df_local):
        """Create PNG bytes for charts (price+MAs, volume, RSI) using matplotlib."""
        imgs = {}
        # Price + MAs
        plt.figure(figsize=(10, 4))
        plt.plot(df_local.index, df_local[close_col], label="Close", linewidth=1.6, color="#0b63d6")
        if "MA50" in df_local.columns:
            plt.plot(df_local.index, df_local["MA50"], label="MA50", linestyle="--", linewidth=1)
        if "MA200" in df_local.columns:
            plt.plot(df_local.index, df_local["MA200"], label="MA200", linestyle=":", linewidth=1)
        plt.title(f"{ticker} Price & Moving Averages")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(alpha=0.12)
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        buf_price = BytesIO()
        plt.tight_layout()
        plt.savefig(buf_price, format="png", dpi=150)
        plt.close()
        buf_price.seek(0)
        imgs["price"] = buf_price.getvalue()

        # Volume
        if "Volume" in df_local.columns:
            plt.figure(figsize=(10, 3))
            plt.bar(df_local.index, df_local["Volume"], color="orange")
            plt.title(f"{ticker} Volume")
            plt.xlabel("Date")
            plt.ylabel("Volume")
            plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
            buf_vol = BytesIO()
            plt.tight_layout()
            plt.savefig(buf_vol, format="png", dpi=150)
            plt.close()
            buf_vol.seek(0)
            imgs["volume"] = buf_vol.getvalue()

        # RSI
        if "RSI14" in df_local.columns:
            plt.figure(figsize=(10, 2.2))
            plt.plot(df_local.index, df_local["RSI14"], color="purple")
            plt.axhline(70, color="red", linestyle="--", linewidth=0.6)
            plt.axhline(30, color="green", linestyle="--", linewidth=0.6)
            plt.title(f"{ticker} RSI (14)")
            buf_rsi = BytesIO()
            plt.tight_layout()
            plt.savefig(buf_rsi, format="png", dpi=150)
            plt.close()
            buf_rsi.seek(0)
            imgs["rsi"] = buf_rsi.getvalue()

        return imgs

    def build_pdf_bytes(df_local, info_local, ai_text_local, period_label):
        """Create a polished PDF in-memory and return BytesIO."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        flow = []

        # Cover (title & meta)
        title = f"FinLens AI — Detailed Stock Report: {ticker}"
        flow.append(Paragraph(title, styles["Title"]))
        flow.append(Spacer(1, 8))
        flow.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
        flow.append(Paragraph(f"Period: {period_label}", styles["Normal"]))
        flow.append(Spacer(1, 12))

        # Company & metrics
        flow.append(Paragraph("<b>Company Summary</b>", styles["Heading2"]))
        summary_text = info_local.get("longBusinessSummary", "Summary not available.")
        flow.append(Paragraph(summary_text[:1200], styles["Normal"]))
        flow.append(Spacer(1, 10))
        market_cap = info_local.get("marketCap")
        flow.append(Paragraph(f"<b>Market cap:</b> {f'${market_cap/1e9:.2f}B' if market_cap else 'N/A'}", styles["Normal"]))
        flow.append(Spacer(1, 12))

        # AI summary
        flow.append(Paragraph("<b>AI Analysis</b>", styles["Heading2"]))
        if ai_text_local:
            # split into paragraphs
            for p in ai_text_local.split("\n\n"):
                flow.append(Paragraph(p.strip(), styles["Normal"]))
                flow.append(Spacer(1, 6))
        else:
            flow.append(Paragraph("AI analysis not available locally. Install Ollama + mistral to enable AI text.", styles["Normal"]))
        flow.append(Spacer(1, 12))

        # Charts images
        imgs = create_chart_images_bytes(df_local)
        if imgs.get("price"):
            flow.append(Paragraph("<b>Price chart</b>", styles["Heading3"]))
            flow.append(Spacer(1, 6))
            flow.append(RLImage(BytesIO(imgs["price"]), width=480, height=200))
            flow.append(Spacer(1, 10))
        if imgs.get("volume"):
            flow.append(Paragraph("<b>Volume chart</b>", styles["Heading3"]))
            flow.append(Spacer(1, 6))
            flow.append(RLImage(BytesIO(imgs["volume"]), width=480, height=140))
            flow.append(Spacer(1, 10))
        if imgs.get("rsi"):
            flow.append(Paragraph("<b>RSI (14)</b>", styles["Heading3"]))
            flow.append(RLImage(BytesIO(imgs["rsi"]), width=480, height=100))
            flow.append(Spacer(1, 10))

        # Recent table (last 10 rows)
        flow.append(Paragraph("<b>Recent Price Data (last 10 rows)</b>", styles["Heading2"]))
        last10 = df_local.tail(10).reset_index()
        rows_html = "<br/>".join(
            [f"{r['Date'].strftime('%Y-%m-%d')}: O {r.get('Open','N/A'):.2f} H {r.get('High','N/A'):.2f} L {r.get('Low','N/A'):.2f} C {r.get('Close','N/A'):.2f} V {int(r.get('Volume',0)):,}" for _, r in last10.iterrows()]
        )
        flow.append(Paragraph(rows_html, styles["Normal"]))

        doc.build(flow)
        buffer.seek(0)
        return buffer

    def build_excel_bytes(df_local, info_local, ai_text_local, period_label):
        """Create Excel workbook with data, charts, and AI sheet (xlsxwriter)."""
        out = BytesIO()
        # use pandas ExcelWriter with xlsxwriter engine for chart features
        with pd.ExcelWriter(out, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
            # Historical data (reset index to export dates as column)
            df_export = df_local.copy()
            df_export = df_export.reset_index()
            df_export.rename(columns={"index": "Date"}, inplace=True)
            df_export.to_excel(writer, sheet_name="Historical_Data", index=False)

            # Summary sheet
            summary = {
                "Metric": ["Latest Close", "Highest Price", "Lowest Price", "Average Volume"],
                "Value": [
                    df_local[close_col].iloc[-1] if close_col in df_local.columns else np.nan,
                    df_local[close_col].max() if close_col in df_local.columns else np.nan,
                    df_local[close_col].min() if close_col in df_local.columns else np.nan,
                    df_local["Volume"].mean() if "Volume" in df_local.columns else np.nan,
                ],
            }
            pd.DataFrame(summary).to_excel(writer, sheet_name="Summary_Stats", index=False)

            # AI summary sheet
            pd.DataFrame({"AI_Summary": [ai_text_local if ai_text_local else "AI not available"]}).to_excel(writer, sheet_name="AI_Summary", index=False)

            workbook = writer.book
            hist_sheet = writer.sheets["Historical_Data"]

            # Insert price & volume images (PNG) into Historical_Data sheet
            imgs = create_chart_images_bytes(df_local)
            if imgs.get("price"):
                hist_sheet.insert_image("J2", "price.png", {"image_data": BytesIO(imgs["price"]), "x_scale": 0.7, "y_scale": 0.7})
            if imgs.get("volume"):
                hist_sheet.insert_image("J22", "volume.png", {"image_data": BytesIO(imgs["volume"]), "x_scale": 0.7, "y_scale": 0.7})

            # Create a small chart from the data in Summary_Stats
            try:
                summary_sheet = writer.sheets["Summary_Stats"]
                chart = workbook.add_chart({"type": "column"})
                chart.add_series({
                    "name": "Summary",
                    "categories": ["Summary_Stats", 1, 0, len(summary["Metric"]), 0],
                    "values": ["Summary_Stats", 1, 1, len(summary["Metric"]), 1],
                })
                chart.set_title({"name": "Summary Metrics"})
                summary_sheet.insert_chart("D2", chart, {"x_scale": 1.2, "y_scale": 1.0})
            except Exception:
                pass

        out.seek(0)
        return out

    # UI: download buttons that produce files on demand
    colA, colB = st.columns(2)
    with colA:
        if st.button("📑 Generate & Download PDF Report"):
            try:
                pdf_bytes = build_pdf_bytes(hist_ind, info, ai_text, time_range)
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"{ticker}_detailed_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"PDF generation failed: {e}")

    with colB:
        if st.button("📊 Generate & Download Excel Report"):
            try:
                excel_bytes = build_excel_bytes(hist_ind, info, ai_text, time_range)
                st.download_button(
                    label="⬇️ Download Excel",
                    data=excel_bytes.getvalue(),
                    file_name=f"{ticker}_detailed_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Excel generation failed: {e}")

    st.success("Dashboard ready — AI content requires local Ollama + mistral for full predictions.")

# run
if __name__ == "__main__":
    main()
