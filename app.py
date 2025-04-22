def main():
    st.title("AI Portfolio Manager")
    st.markdown("Real-time market insights, portfolio simulation, and sentiment analysis")

    data_dict = {}

    for name, ticker in {**indexes, **currencies}.items():
        data = fetch_data(ticker, lookback_days)

        if data is None or data.empty or "Close" not in data.columns:
            st.warning(f"Data for {name} ({ticker}) could not be loaded or is missing required fields.")
            continue

        try:
            analysis = analyze_data(data)
            insight = generate_insight(name, analysis)

            st.subheader(f"{name} ({ticker})")
            st.text(insight)
            plot_chart(data, name)

            data_dict[name] = data

        except Exception as e:
            st.error(f"Error analyzing data for {name}: {str(e)}")

    if data_dict:
        st.subheader("Simulate Your Portfolio")
        allocations = {}
        for name in data_dict.keys():
            weight = st.slider(f"{name} Allocation %", 0, 100, 10)
            allocations[name] = weight / 100

        if st.button("Run Simulation"):
            simulate_portfolio(allocations, data_dict)
    else:
        st.info("No valid data to simulate portfolio.")

    st.subheader("Market News Sentiment")
    topic = st.text_input("Enter topic (e.g. Tesla, Oil, USD)", "USD")
    if st.button("Analyze News"):
        fetch_and_analyze_news(topic)
