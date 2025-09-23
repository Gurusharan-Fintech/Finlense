# pages/4_Professional_Dashboard.py
import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Local forecasting
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tools.sm_exceptions import ConvergenceWarning
import warnings
warnings.simplefilter('ignore', ConvergenceWarning)

st.set_page_config(page_title="Professional Dashboard", layout="wide")

# -------------------------
# Helpers: Indicators, Forecast, Analysis
# -------------------------
def compute_indicators(hist):
    """Compute MA20, MA50, RSI(14), volatility (daily std), momentum slope."""
    out = {}
    h = hist.copy()
    h['returns'] = h['Close'].pct_change()
    out['ma20'] = h['Close'].rolling(window=20).mean().iloc[-1] if len(h) >= 20 else np.nan
    out['ma50'] = h['Close'].rolling(window=50).mean().iloc[-1] if len(h) >= 50 else np.nan
    out['volatility_daily'] = h['returns'].std()
    out['volatility_annual'] = out['volatility_daily'] * np.sqrt(252) if not np.isnan(out['volatility_daily']) else np.nan

    # RSI(14)
    period = 14
    delta = h['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    # Wilder smoothing (simple rolling mean here)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    out['rsi'] = rsi.iloc[-1] if len(rsi) >= period else np.nan

    # Momentum: linear slope of log price over last 30 days
    window = min(30, len(h))
    if window >= 3:
        y = np.log(h['Close'].tail(window).values)
        x = np.arange(window)
        slope = np.polyfit(x, y, 1)[0]
        out['momentum_slope'] = slope
    else:
        out['momentum_slope'] = np.nan

    # Latest close and pct change over selected window (30 days)
    out['last_close'] = h['Close'].iloc[-1]
    if len(h) >= 30:
        out['pct_30d'] = (h['Close'].iloc[-1] / h['Close'].iloc[-30] - 1) * 100
    else:
        out['pct_30d'] = (h['Close'].iloc[-1] / h['Close'].iloc[0] - 1) * 100 if len(h) > 1 else 0

    return out

def forecast_arima(series, periods=30):
    """Forecast `periods` future business days using ARIMA(1,1,1) fallback logic.
       Returns forecast_index, forecast_mean (np.array), lower_ci, upper_ci, success_flag."""
    # Clean series: dropna
    s = series.dropna().astype(float).copy()
    # Ensure index is timezone naive
    if hasattr(s.index, "tz") and s.index.tz is not None:
        s.index = s.index.tz_localize(None)
    # Use daily business day index for forecast points
    last_date = s.index[-1]
    try:
        # If series too short, fallback
        if len(s) < 10:
            raise ValueError("Series too short for ARIMA fit")
        # Fit ARIMA(1,1,1)
        model = ARIMA(s, order=(1, 1, 1))
        fitted = model.fit()
        pred = fitted.get_forecast(steps=periods)
        mean = pred.predicted_mean
        ci = pred.conf_int(alpha=0.05)  # DataFrame with lower, upper
        lower = ci.iloc[:, 0].values
        upper = ci.iloc[:, 1].values
        # Forecast index: next business days
        forecast_index = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=periods)
        return forecast_index, mean.values, lower, upper, True
    except Exception:
        # fallback: constant forecast (last observed value)
        mean_val = np.repeat(s.iloc[-1], periods)
        lower = mean_val * 0.995
        upper = mean_val * 1.005
        forecast_index = pd.bdate_range(start=last_date + pd.Timedelta(days=1), periods=periods)
        return forecast_index, mean_val, lower, upper, False

def generate_analysis(info, indicators, forecast_mean, forecast_index, forecast_success):
    """Create a long, professional analysis paragraph and a short prediction summary."""
    comp = info.get('shortName') or info.get('longName') or "This company"
    sector = info.get('sector', 'N/A')
    market_cap = info.get('marketCap', None)
    trailing_pe = info.get('trailingPE', None)
    revenue = info.get('totalRevenue', None) or info.get('revenue', None)

    # Format numbers
    mc_text = f"${market_cap/1e9:.1f}B" if market_cap else "N/A"
    pe_text = f"{trailing_pe:.2f}" if trailing_pe else "N/A"

    # Indicators
    ma20 = indicators.get('ma20', np.nan)
    ma50 = indicators.get('ma50', np.nan)
    rsi = indicators.get('rsi', np.nan)
    vol_ann = indicators.get('volatility_annual', np.nan)
    last_close = indicators.get('last_close', np.nan)
    pct_30d = indicators.get('pct_30d', np.nan)
    slope = indicators.get('momentum_slope', np.nan)

    # Trend interpretation
    ma_signal = "neutral"
    if not np.isnan(ma20) and not np.isnan(ma50):
        ma_signal = "bullish" if ma20 > ma50 else "bearish"

    rsi_signal = "neutral"
    if not np.isnan(rsi):
        if rsi > 70:
            rsi_signal = "overbought"
        elif rsi < 30:
            rsi_signal = "oversold"
        else:
            rsi_signal = "neutral"

    vol_signal = "low"
    if not np.isnan(vol_ann):
        if vol_ann > 0.6:
            vol_signal = "high"
        elif vol_ann > 0.25:
            vol_signal = "moderate"
        else:
            vol_signal = "low"

    # Forecast summary (last forecasted point)
    if len(forecast_mean) > 0:
        predicted_end = forecast_mean[-1]
        pct_change_pred = (predicted_end / last_close - 1) * 100 if last_close and last_close != 0 else 0
        pred_trend = "up" if pct_change_pred > 0 else "down" if pct_change_pred < 0 else "flat"
    else:
        predicted_end = None
        pct_change_pred = 0
        pred_trend = "flat"

    # Success note
    model_note = "Model-based ARIMA forecast" if forecast_success else "Fallback (simple) forecast due to limited data or model convergence."

    # Build long paragraph (3+ paragraphs)
    paragraphs = []

    p1 = (
        f"{comp} operates in the {sector} sector with a market capitalization of {mc_text} and a trailing P/E of {pe_text}. "
        f"Over the selected period the stock's closing price is {last_close:.2f} (latest) and the price moved approximately {pct_30d:+.2f}% over the prior window. "
    )
    paragraphs.append(p1)

    p2 = (
        f"Technical indicators show a {ma_signal} signal (20-day MA = {ma20:.2f}, 50-day MA = {ma50:.2f}) and RSI at {rsi:.1f}, which is interpreted as {rsi_signal}. "
        f"Annualized volatility is {vol_ann:.2%} which is considered {vol_signal}. Momentum slope (log price) is {slope:.6f}, indicating the short-term trend strength."
    )
    paragraphs.append(p2)

    p3 = (
        f"The forecasting engine ({model_note}) estimates a {pred_trend} trend over the next {len(forecast_mean)} business days. "
        f"Model end-point prediction is approximately {predicted_end:.2f}, representing a {pct_change_pred:+.2f}% change from the latest close. "
        f"Forecasts include uncertainty — treat the central estimate as a point prediction and use the chart's confidence band for risk assessment."
    )
    paragraphs.append(p3)

    # Reasons & Drivers bullets
    reasons = []
    if ma_signal == "bullish":
        reasons.append("Short-term momentum is positive because the 20-day MA sits above the 50-day MA.")
    else:
        reasons.append("Short-term momentum appears weak since the 20-day MA is below the 50-day MA.")

    if rsi_signal == "overbought":
        reasons.append("RSI indicates the stock may be overbought in the short term (possible pullback risk).")
    elif rsi_signal == "oversold":
        reasons.append("RSI indicates the stock may be oversold (potential rebound opportunity).")

    if vol_signal == "high":
        reasons.append("High volatility suggests larger price swings and higher risk.")
    elif vol_signal == "low":
        reasons.append("Low volatility suggests relatively calmer price action.")

    # Valuation based reason
    if trailing_pe and trailing_pe < 10:
        reasons.append("Valuation is relatively low compared to typical market P/E, which may indicate value potential.")
    elif trailing_pe and trailing_pe > 40:
        reasons.append("Valuation is relatively high, which can increase downside risk if growth expectations slip.")

    # Compose full text
    analysis_text = "\n\n".join(paragraphs)
    analysis_text += "\n\n**Possible reasons / drivers:**\n"
    for r in reasons:
        analysis_text += f"- {r}\n"

    analysis_text += (
        "\n\n**Prediction summary:**\n"
        f"- Central forecast (final point): {predicted_end:.2f}\n"
        f"- Expected change vs latest close: {pct_change_pred:+.2f}%\n"
        f"- Forecast method: {model_note}\n\n"
        "**Disclaimer:** This is model-based analysis for educational/demonstration purposes, not financial advice."
    )

    return analysis_text, {
        "predicted_end": predicted_end,
        "pct_change_pred": pct_change_pred,
        "model_used": model_note,
        "ma_signal": ma_signal,
        "rsi": rsi,
        "vol_ann": vol_ann
    }

# -------------------------
# Page UI start
# -------------------------
# Show chosen stock (read-only) from homepage
if "selected_stock" in st.session_state and st.session_state["selected_stock"]:
    ticker = st.session_state["selected_stock"]
    st.markdown(f"### 📌 Selected Stock: **{ticker}**")
else:
    st.warning("⚠️ Please choose a stock from the home page first.")
    st.stop()

# Period selection (reuse)
time_range = st.selectbox("Growth Period", ["1mo", "3mo", "6mo", "1y", "5y", "max"], index=3)

# Load data
try:
    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period=time_range)
    # Ensure timezone naive index
    if hasattr(hist.index, "tz") and hist.index.tz is not None:
        hist.index = hist.index.tz_localize(None)

    if hist.empty:
        st.error("No historical data returned for this ticker/time-range.")
        st.stop()

    # Compute indicators
    indicators = compute_indicators(hist)

    # Forecast (30 business days) — make horizon selectable if desired
    forecast_horizon = 30
    forecast_idx, forecast_mean, forecast_lower, forecast_upper, success_flag = forecast_arima(hist['Close'], periods=forecast_horizon)

    # Generate analysis text
    analysis_text, analysis_meta = generate_analysis(info, indicators, forecast_mean, forecast_idx, success_flag)

    # Layout: Analysis (left) & Forecast Chart (right)
    st.markdown("---")
    a_col, c_col = st.columns([1.4, 2])

    with a_col:
        st.subheader("🤖 Automated Analysis & Prediction (local model)")
        st.markdown(analysis_text, unsafe_allow_html=True)

        # Show compact metric cards
        st.markdown("### Key quick metrics")
        k1, k2, k3 = st.columns(3)
        k1.metric("Latest Close", f"{indicators['last_close']:.2f}")
        k2.metric("30d change", f"{indicators['pct_30d']:+.2f}%")
        k3.metric("RSI (14)", f"{indicators['rsi']:.1f}" if not np.isnan(indicators['rsi']) else "N/A")

    with c_col:
        st.subheader(f"📈 Forecast ({forecast_horizon} business days)")
        # Build forecast dataframe
        hist_df = hist[['Close']].copy().rename(columns={'Close': 'Actual'})
        forecast_df = pd.DataFrame({
            'Forecast': forecast_mean,
            'Lower': forecast_lower,
            'Upper': forecast_upper
        }, index=forecast_idx)

        # Concatenate for plotting convenience
        plot_df_hist = hist_df.tail(250)  # show last 250 points to keep plot responsive
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=plot_df_hist.index, y=plot_df_hist['Actual'], mode='lines', name='Actual'))
        fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df['Forecast'], mode='lines', name='Forecast', line=dict(color='royalblue', dash='dash')))
        # confidence band
        fig.add_trace(go.Scatter(
            x=np.concatenate([forecast_df.index, forecast_df.index[::-1]]),
            y=np.concatenate([forecast_df['Upper'], forecast_df['Lower'][::-1]]),
            fill='toself',
            fillcolor='rgba(0,100,200,0.15)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="skip",
            showlegend=True,
            name='Confidence band'
        ))
        fig.update_layout(template='plotly_white', xaxis_title='Date', yaxis_title='Price', height=450)
        st.plotly_chart(fig, use_container_width=True)

        # Small numeric forecast summary
        last_pred = forecast_mean[-1]
        pct_change_pred = analysis_meta['pct_change_pred']
        st.markdown("**Forecast summary**")
        st.write(f"- Central forecast (end): **{last_pred:.2f}**")
        st.write(f"- Expected % change vs latest close: **{pct_change_pred:+.2f}%**")
        st.write(f"- Model: **{analysis_meta['model_used']}**")

    # (Existing charts below — keep them compact)
    st.markdown("---")
    st.subheader("Additional charts")
    low_col, high_col = st.columns(2)

    with low_col:
        st.subheader("📊 Key Ratios (if available)")
        metrics = {
            "PE Ratio": info.get("trailingPE"),
            "Price-to-Book": info.get("priceToBook"),
            "Profit Margin": info.get("profitMargins"),
            "Return on Equity": info.get("returnOnEquity"),
        }
        filtered_metrics = {k: v for k, v in metrics.items() if v is not None}
        if filtered_metrics:
            metrics_df = pd.DataFrame(list(filtered_metrics.items()), columns=["Metric", "Value"])
            fig_metric = px.bar(metrics_df, x='Metric', y='Value', color='Metric', title="Key Ratios")
            st.plotly_chart(fig_metric, use_container_width=True)
        else:
            st.info("No financial metrics available for this stock.")

    with high_col:
        st.subheader("📊 Volume traded (recent)")
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(x=hist.index, y=hist['Volume'], marker_color='orange'))
        fig_vol.update_layout(template='plotly_white', xaxis_title='Date', yaxis_title='Volume', height=350)
        st.plotly_chart(fig_vol, use_container_width=True)

    # Keep Quick Actions (PDF + Excel) — unchanged but safe
    st.markdown("---")
    st.subheader("⚡ Quick Actions")
    colA, colB = st.columns(2)

    with colA:
        def create_pdf_buffer():
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(180, 750, f"{info.get('shortName', ticker)} Stock Report")
            c.setFont("Helvetica", 11)
            c.drawString(50, 730, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(50, 715, f"Stock: {ticker}   Time Range: {time_range}")
            y = 690
            c.setFont("Helvetica-Bold", 13)
            c.drawString(50, y, "Key Metrics")
            c.setFont("Helvetica", 11)
            y -= 16
            c.drawString(50, y, f"Latest Close: {indicators['last_close']:.2f}")
            y -= 14
            c.drawString(50, y, f"30d Change: {indicators['pct_30d']:+.2f}%")
            y -= 14
            c.drawString(50, y, f"RSI(14): {indicators['rsi']:.1f}")
            y -= 20
            c.drawString(50, y, "Forecast Summary:")
            y -= 14
            c.drawString(50, y, f"Predicted end price (central): {forecast_mean[-1]:.2f}")
            y -= 30
            c.drawString(50, y, "Analysis (summary):")
            y -= 14
            summary_text = analysis_text.split('\n\n')[0]
            # write a few lines
            for line in summary_text.split('. '):
                if y < 100:
                    c.showPage()
                    y = 750
                c.drawString(50, y, line.strip()[:120])
                y -= 12
            c.showPage()
            c.save()
            buffer.seek(0)
            return buffer

        pdf_buf = create_pdf_buffer()
        st.download_button(
            label="📑 Download as PDF",
            data=pdf_buf,
            file_name=f"{ticker}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )

    with colB:
        try:
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                hist_export = hist.copy()
                if hist_export.index.tz is not None:
                    hist_export.index = hist_export.index.tz_localize(None)
                hist_export.index.name = "Date"
                hist_export.to_excel(writer, sheet_name="Historical_Data")
                # Summary sheet
                summary_stats = pd.DataFrame({
                    'Metric': ['Latest Close', 'Highest Price', 'Lowest Price', 'Average Close', 'Total Volume'],
                    'Value': [
                        f"{indicators['last_close']:.2f}",
                        f"{hist['High'].max():.2f}",
                        f"{hist['Low'].min():.2f}",
                        f"{hist['Close'].mean():.2f}",
                        f"{hist['Volume'].sum():,.0f}"
                    ]
                })
                summary_stats.to_excel(writer, sheet_name='Summary_Stats', index=False)
            st.download_button(
                label="📊 Download as Excel",
                data=excel_buffer.getvalue(),
                file_name=f"{ticker}_data_{time_range}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"❌ Error creating Excel file: {str(e)}")

else:
    st.error("No historical data found.")
