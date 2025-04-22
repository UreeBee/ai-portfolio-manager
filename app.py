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
    portfolio_return = pd.DataFrame(returns).sum(axis=1).cumsum()
    st.line_chart(portfolio_return)

# ==== NEWS SENTIMENT ANALYSIS ====
def fetch_and_analyze_news(query):
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey=YOUR_NEWSAPI_KEY"
    response = requests.get(url)
    articles = response.json().get("articles", [])[:5]
    st.subheader("News Sentiment")
    for article in articles:
        title = article['title']
        sentiment = TextBlob(title).sentiment.polarity
        st.write(f"{title} (Sentiment: {round(sentiment, 2)})")

# ==== STREAMLIT DASHBOARD ====
def main():
    st.title("AI Portfolio Manager")
    st.markdown("Real-time market insights, portfolio simulation, and sentiment analysis")

    data_dict = {}

    for name, ticker in {**indexes, **currencies}.items():
        data = fetch_data(ticker, lookback_days)
        if data.empty:
            continue

        analysis = analyze_data(data)
        insight = generate_insight(name, analysis)

        st.subheader(f"{name} ({ticker})")
        st.text(insight)
        plot_chart(data, name)

        data_dict[name] = data

    st.subheader("Simulate Your Portfolio")
    allocations = {}
    for name in data_dict.keys():
        weight = st.slider(f"{name} Allocation %", 0, 100, 10)
        allocations[name] = weight / 100

    if st.button("Run Simulation"):
        simulate_portfolio(allocations, data_dict)

    st.subheader("Market News Sentiment")
    topic = st.text_input("Enter topic (e.g. Tesla, Oil, USD)", "USD")
    if st.button("Analyze News"):
        fetch_and_analyze_news(topic)

if __name__ == "__main__":
    main()
