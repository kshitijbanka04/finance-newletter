import os
from agents.news_agent import NewsAgent

def test_news_agent():
    # Stock and sector details
    stock_name = "Reliance Industries"
    sector_name = "Conglomerate"

    # API keys
    tavily_api_key = os.getenv("TAVILY_API_KEY")  # Set your Tavily API key
    exa_api_key = os.getenv("EXA_API_KEY")        # Set your Exa API key
    fallback_api_key = os.getenv("FALLBACK_NEWS_API_KEY")  # Set your NewsAPI key

    # Initialize the NewsAgent
    agent = NewsAgent(stock_name, sector_name, tavily_api_key, exa_api_key, fallback_api_key)

    # Run the agent to fetch news
    news_results = agent.run()

    # Print stock-specific news results
    print("\nRaw Stock-Specific News Results:")
    for i, result in enumerate(news_results["stock_news"], start=1):
        print(f"\nResult {i}:\n{result}\n")

    # Print sector-specific news results
    print("\nRaw Sector-Specific News Results:")
    for i, result in enumerate(news_results["sector_news"], start=1):
        print(f"\nResult {i}:\n{result}\n")

if __name__ == "__main__":
    # Run the test
    test_news_agent()
