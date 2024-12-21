from openai import OpenAI
import os

class NewsletterAgent:
    def __init__(self, stock_data_files, openai_api_key):
        """
        Initializes the NewsletterAgent.
        :param stock_data_files: Dictionary containing the raw data for each stock.
        :param openai_api_key: OpenAI API key for GPT-based generation.
        """
        self.stock_data_files = stock_data_files  # { "Reliance": "text_data", "Infosys": "text_data" }
        self.openai_api_key = openai_api_key

    def generate_prompt(self, stock_name, stock_data):
        """
        Creates a structured prompt for generating the newsletter.
        """
        return f"""
        You are a financial analyst and newsletter expert. Write a brief, professional newsletter section about the company "{stock_name}" using the provided data.

        ### **Instructions**
        - Summarize the key updates for "{stock_name}" in a readable and engaging way.
        - Ensure the response includes but not restrained to (Below are headings so we can have multiple subpoints under them):
          1. **Key Company Updates including numbers** (e.g., major actions, financial highlights, achievements).
          2. **Industry and Market Trends** (e.g., sector trends, regulatory changes).
          3. **Challenges and Opportunities** (e.g., risks, growth prospects).
          4. **Recommendations** (buy, hold, sell with reasons).
          5. Provide **resources and links** if applicable.

        ### **Stock Data based on financial, corporate action, organization heirarchy, business strategic decision**
        {stock_data}

        ### **Output Format**
        - Use concise headings (e.g., **Key Updates**, **Market Trends**, etc.).
        - Write in human-readable, engaging language.
        - Ensure each section is clear and professional.
        """

    def query_llm(self, prompt):
        """
        Sends the prompt to OpenAI GPT and returns the response.
        """
        client = OpenAI(api_key=self.openai_api_key)
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert financial analyst."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

    def generate_newsletter(self):
        """
        Processes the data for each stock and generates the final newsletter.
        """
        newsletter_sections = []

        for stock_name, stock_data in self.stock_data_files.items():
            print(f"Generating newsletter for {stock_name}...")
            prompt = self.generate_prompt(stock_name, stock_data)
            response = self.query_llm(prompt)
            newsletter_sections.append(f"### {stock_name}\n{response}")

        return "\n\n".join(newsletter_sections)
