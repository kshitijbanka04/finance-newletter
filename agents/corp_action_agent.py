from openai import OpenAI

class CorpActionsAgent:
    def __init__(self, corp_action_files, api_key):
        self.corp_action_files = corp_action_files
        self.analysis = []
        self.api_key = api_key

    def analyze_file(self, file):
        file_name = file.get("file_name", "")
        file_sub_category = file.get("file_sub_category", "")
        pdf_url = file.get("pdf_file_url", "")
        publish_date = file.get("publish_date", "")
        short_description = file.get("short_description", "")

        summary = self.generate_summary(
            file_name, file_sub_category, pdf_url, publish_date, short_description
        )
        return summary

    def generate_summary(self, file_name, file_sub_category, pdf_url, publish_date, short_description):
        prompt = f"""
        You are a financial expert specializing in corporate actions.

        **Document Details**:
        - **Title**: {file_name}
        - **Category**: {file_sub_category}
        - **Publish Date**: {publish_date}
        - **Short Description**: {short_description if short_description else "N/A"}
        - **URL**: {pdf_url}

        **Instructions**:
        1. Provide a concise summary of the corporate action (e.g., Bonus, Dividend, Record Date).
        2. Highlight the financial implications for stakeholders (e.g., impact on share price, shareholder value).
        3. Identify any timeline or procedural details mentioned in the document.
        4. Offer actionable insights for investors and stakeholders.

        Ensure your response is precise and easy to understand.
        """
        return self.query_openai(prompt)

    def query_openai(self, prompt):
        client = OpenAI(api_key=self.api_key)
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a financial expert.."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

    def run(self):
        for file in self.corp_action_files:
            summary = self.analyze_file(file)
            self.analysis.append(summary)
        return self.analysis
