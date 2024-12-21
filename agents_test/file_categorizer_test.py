import json
from agents.file_categorizer import FileCategorizer
from agents.supervisor_agent import SupervisorAgent
import os
import sys


project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_dir)

open_ai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
exa_api_key = os.getenv("EXA_API_KEY")
fallback_news_api_key = os.getenv("FALLBACK_NEWS_API_KEY")

example_file_path = os.path.join(project_dir, "agents_test", "reliance_example.json")

with open(example_file_path, "r") as file:
    reliance_files = json.load(file)

# Categorize the files
file_categorizer = FileCategorizer(reliance_files)
categorized_files = file_categorizer.categorize_files()

# Print the categorized files
for category, files in categorized_files.items():
    print(f"\n--- {category.upper()} FILES ---")
    for file in files:
        print(file["file_name"])

api_keys = {
    "openai": open_ai_api_key,
    "tavily": tavily_api_key,
    "exa": exa_api_key,
    "fallback": fallback_news_api_key,
}

# Initialize and run the SupervisorAgent
supervisor = SupervisorAgent(
    categorized_files=categorized_files, 
    stock_name="Reliance Industries", 
    sector_name="Conglomerate", 
    api_keys=api_keys
)

final_results = supervisor.run()

# Print the consolidated results
for category, result in final_results.items():
    print(f"\n--- {category.upper()} RESULTS ---\n")
    print(result)

