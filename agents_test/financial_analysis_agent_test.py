import sys
import os
import json

# Add the project directory to sys.path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_dir)

from agents.financial_analysis_agent import FinancialAnalysisAgent

open_ai_key = os.getenv("OPENAI_API_KEY")

# Use the absolute path for the example.json file
example_file_path = os.path.join(project_dir, "agents_test", "example.json")

with open(example_file_path, "r") as file:
    financial_files = json.load(file)

# Instantiate and run the FinancialAnalysisAgent
agent = FinancialAnalysisAgent(financial_files, open_ai_key)
analysis_results = agent.run()

# Display results
for result in analysis_results:
    print(result)

