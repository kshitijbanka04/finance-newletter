import requests
import os
from tavily import TavilyClient
from exa_py import Exa


class NewsAgent:
    def __init__(self, stock_name, sector_name, tavily_api_key=None, exa_api_key=None, fallback_api_key=None):
        self.stock_name = stock_name
        self.sector_name = sector_name
        self.tavily_api_key = tavily_api_key
        self.exa_api_key = exa_api_key
        self.fallback_api_key = fallback_api_key
        self.stock_news = []
        self.sector_news = []
        self.news_stock_query = f"""
            Fetch comprehensive news data for stock '{self.stock_name}':
            - Quarterly revenue growth over the past year.
            - Profit margins and their variations.
            - Revenue contribution from different commodities or segments.
            - Updates on investments, partnerships, and expansions.
        """
        self.sector_news_query = f"""
            Fetch comprehensive news data for sector '{self.sector_name}':
            - Sector-wide revenue trends and major contributors.
            - Emerging market trends and challenges.
            - Regulatory changes affecting the sector.
            - Comparative data with key competitors.
            """

    def fetch_from_tavily(self, query):
        """
        Fetches news from Tavily.
        """
        tavily_client = TavilyClient(api_key=self.tavily_api_key)
        try:
            context = tavily_client.search(query=query)
            return context.get("results", [])
        except Exception as e:
            print(f"Error fetching Tavily news: {e}")
            return []

    def fetch_from_exa(self, query):
        """
        Fetches news from Exa.
        """
        exa_client = Exa(self.exa_api_key)
        try:
            result = exa_client.search(
                query,
                use_autoprompt=True,
                num_results=2,
                category="news"
            )

            return result.get("results", [])
        except Exception as e:
            print(f"Error fetching Exa news: {e}")
            return []

    def fetch_from_fallback(self, query):
        """
        Fetches news from a fallback service (e.g., newsapi.org).
        """
        try:
            url = f"https://newsapi.org/v2/everything?q={query}&apiKey={self.fallback_api_key}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get("articles", [])
            else:
                print(f"Fallback request failed: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"Error fetching fallback news: {e}")
            return []

    def fetch_news(self, query):
        """
        Tries fetching news in the following order:
        1. Tavily
        2. Exa
        3. Fallback
        """
        if self.tavily_api_key:
            print(f"Fetching {query} news from Tavily...")
            news = self.fetch_from_tavily(query)
            if news:
                return news

        if self.exa_api_key:
            print(f"Fetching {query} news from Exa...")
            news = self.fetch_from_exa(query)
            if news:
                return news

        if self.fallback_api_key:
            print(f"Fetching {query} news from fallback (e.g., newsapi.org)...")
            return self.fetch_from_fallback(query)

        print("No valid API keys provided. Unable to fetch news.")
        return []

    def run(self):
        """
        Fetches stock-specific and sector-specific news.
        """
        print(f"Fetching recent news for stock: {self.stock_name}")
        self.stock_news = self.fetch_news(self.news_stock_query)

        if(self.sector_name.lower()!= "conglomerate"):
            print(f"Fetching recent news for sector {self.sector_name} and somewhat related to {self.stock_name}")
            self.sector_news = self.fetch_news(self.sector_news_query)

        return {"stock_news": self.stock_news, "sector_news": self.sector_news}
