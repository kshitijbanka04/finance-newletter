from concurrent.futures import ThreadPoolExecutor, as_completed
from agents.financial_analysis_agent import FinancialAnalysisAgent
from agents.strategic_update_agent import StrategicUpdatesAgent
from agents.corp_action_agent import CorpActionsAgent
from agents.org_update_agent import OrganizationalUpdatesAgent
from agents.news_agent import NewsAgent

class SupervisorAgent:
    def __init__(self, categorized_files, stock_name, sector_name, api_keys):
        """
        Initializes the SupervisorAgent.
        :param categorized_files: Categorized files for processing.
        :param stock_name: Name of the stock.
        :param sector_name: Name of the sector.
        :param api_keys: Dictionary containing API keys for the agents.
        """
        self.categorized_files = categorized_files
        self.stock_name = stock_name
        self.sector_name = sector_name
        self.api_keys = api_keys
        self.results = {}

    def execute_agent(self, agent_class, *args, **kwargs):
        """
        Helper function to execute an agent and return its results.
        """
        agent = agent_class(*args, **kwargs)
        return agent.run()

    def run(self):
        """
        Executes all agents in parallel and consolidates results.
        """
        # Initialize thread pool
        with ThreadPoolExecutor() as executor:
            # Tasks for each agent
            futures = {
                executor.submit(self.execute_agent, FinancialAnalysisAgent, self.categorized_files["Financial Analysis"], self.api_keys["openai"]): "financial",
                executor.submit(self.execute_agent, StrategicUpdatesAgent, self.categorized_files["Strategic Updates"], self.api_keys["openai"]): "strategic",
                executor.submit(self.execute_agent, CorpActionsAgent, self.categorized_files["Corp. Actions"], self.api_keys["openai"]): "corp_action",
                executor.submit(self.execute_agent, OrganizationalUpdatesAgent, self.categorized_files["Organizational Updates"], self.api_keys["openai"]): "org_update",
                executor.submit(self.execute_agent, NewsAgent, self.stock_name, self.sector_name, self.api_keys["tavily"], self.api_keys["exa"], self.api_keys["fallback"]): "news",
            }

            # Gather results as they complete
            for future in as_completed(futures):
                agent_name = futures[future]
                try:
                    self.results[agent_name] = future.result()
                except Exception as e:
                    self.results[agent_name] = f"Error in {agent_name} agent: {e}"

        print(self.results)
        return self.results
