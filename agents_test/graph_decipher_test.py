# Initialize the visualizer with OpenAI API key
import json
from agents.visualizer_agent import StockVisualizer
import sys, os

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_dir)

open_ai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
exa_api_key = os.getenv("EXA_API_KEY")
fallback_news_api_key = os.getenv("FALLBACK_NEWS_API_KEY")

visualizer = StockVisualizer(api_key=open_ai_api_key, tavily_api_key=tavily_api_key)

# Load text data
file_path = "/Users/kshitijbanka/finance-newletter/stock_reports/HDFC_Bank.txt"
with open(file_path, 'r', encoding='utf-8') as file:
    text_data = file.read()

# Generate final graph configurations
stock_name = "HDFC Bank"
final_configs = visualizer.generate_final_config(text_data, stock_name)

print(final_configs)

