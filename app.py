import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.title("Stock Trend Visualizer")

# Input stock ticker
ticker = st.text_input("Enter Stock Symbol (e.g., AAPL):")

# Input date range
start_date = st.date_input("Start date", pd.to_datetime("2025-01-01"))
end_date = st.date_input("End date", pd.to_datetime("today"))

if ticker:
    # Fetch data
    data = yf.download(ticker, start=start_date, end=end_date)
    
    if not data.empty:
        st.subheader(f"{ticker} Closing Price")
        plt.figure(figsize=(10,5))
        plt.plot(data['Close'], label="Close Price")
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.legend()
        st.pyplot(plt)
        
        # Moving averages
        data['MA20'] = data['Close'].rolling(window=20).mean()
        data['MA50'] = data['Close'].rolling(window=50).mean()
        
        st.subheader(f"{ticker} Closing Price with Moving Averages")
        plt.figure(figsize=(10,5))
        plt.plot(data['Close'], label="Close")
        plt.plot(data['MA20'], label="20-day MA")
        plt.plot(data['MA50'], label="50-day MA")
        plt.legend()
        st.pyplot(plt)
        
        # Buy/Sell signals
        signals = []
        for i in range(1, len(data)):
            if data['MA20'].iloc[i] > data['MA50'].iloc[i] and data['MA20'].iloc[i-1] <= data['MA50'].iloc[i-1]:
                signals.append(f"Buy signal on {data.index[i].date()}")
            elif data['MA20'].iloc[i] < data['MA50'].iloc[i] and data['MA20'].iloc[i-1] >= data['MA50'].iloc[i-1]:
                signals.append(f"Sell signal on {data.index[i].date()}")
        if signals:
            st.subheader("Trend Alerts")
            for s in signals:
                st.write(s)
    else:
        st.write("No data found for this ticker.")
