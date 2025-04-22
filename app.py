import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import openai
import matplotlib.pyplot as plt
import streamlit as st
from textblob import TextBlob
import requests

# ==== CONFIGURATION ====
openai.api_key = "YOUR_OPENAI_API_KEY"
indexes = {
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Dow Jones": "^DJI"
}
currencies = {
    "USD/ZAR": "ZAR=X",
    "EUR/USD": "EURUSD=X"
}
lookback_days = 5

# ==== DATA FETCHER ====
def fetch_data(ticker, days):
    end = datetime.today()
    start = end - timedelta(days=days)
    data = yf.download(ticker, start=start, end=end, interval="1h")
    return data

# ==== ANALYSIS ====
def analyze_data(data):
    recent = data["Close"][-1]
    prev = data["Close"][-2]
    pct_change = ((recent - prev) / prev) * 100
    ma5 = data["Close"].rolling(window=5).mean().iloc[-1]
    return {
        "current": recent,
        "previous": prev,
        "change_pct": round(pct_change, 2),
        "ma5": round(ma5, 2)
    }

# ==== GPT INSIGHT GENERATOR ====
def generate_insight(name, analysis):
    prompt = f"""
You are a top-performing hedge fund manager.
Based on this data:
Name: {name}
Current Price: {analysis['current']}
Previous Price: {analysis['previous']}
% Change: {analysis['change_pct']}%
5-Hour Moving Average: {analysis['ma5']}

Generate a professional investment insight.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a world-class portfolio manager."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# ==== CHART VISUALIZER ====
def plot_chart(data, name):
    plt.figure(figsize=(10, 4))
    plt.plot(data['Close'], label="Close Price")
    plt.title(f"{name} - Price Chart")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)

# ==== PORTFOLIO SIMULATOR ====
def simulate_portfolio(allocations, data_dict):
    returns = {}
    for name, weight in allocations.items():
        data = data_dict[name]
        pct_change = data['Close'].pct_change().dropna()
        returns[name] = pct_change * weight
    portfolio_return = pd.DataFrame(returns).sum(axis=1_
