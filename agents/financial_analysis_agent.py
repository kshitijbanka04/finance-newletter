from openai import OpenAI
import os

class FinancialAnalysisAgent:
    def __init__(self, financial_files, api_key):
        self.financial_files = financial_files
        self.analysis = []  
        self.api_key = api_key

    def analyze_file(self, file):
        file_name = file.get("file_name", "Unknown")
        file_sub_category = file.get("file_sub_category", "Unknown")
        pdf_url = file.get("pdf_file_url", "N/A")
        publish_date = file.get("publish_date", "N/A")
        short_description = file.get("short_description", "N/A")

        analysis_summary = self.generate_summary(
            file_name, file_sub_category, pdf_url, publish_date, short_description
        )

        return {
            "file_name": file_name,
            "publish_date": publish_date,
            "file_url": pdf_url,
            "analysis_summary": analysis_summary
        }

    def generate_summary(self, file_name, file_sub_category, pdf_url, publish_date, short_description):
        # Comprehensive prompt for financial analysis
        prompt = f"""
        You are an expert financial analyst specializing in Indian markets. Your task is to analyze the given financial document and generate a detailed report.

        **Document Details**:
        - **Title**: {file_name}
        - **Category**: {file_sub_category}
        - **Publish Date**: {publish_date}
        - **Short Description**: {short_description if short_description else "N/A"}
        - **URL**: {pdf_url}

        **Instructions**:
        1. Summarize the document’s key highlights and main points.
        2. Extract financial metrics (e.g., revenue, profit margins, cash flow).
        3. Analyze trends, risks, opportunities, and forward-looking statements.
        4. Highlight any red flags or discrepancies (e.g., contingent liabilities, litigation).
        5. Provide actionable insights for investors (e.g., hold, buy, sell recommendations).

        NOTE: Do not miss out business numbers, percentages they are very important. Do not give response like The company reported a year-on-year revenue growth of X%, reaching INR XX billion. The number shouldnt be missed.

        Ensure your response is professional, concise, and suitable for inclusion in a financial newsletter but not too short.
        """
        return self.query_openai(prompt)

    def query_openai(self, prompt):
        client = OpenAI(api_key=self.api_key)
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

    def run(self):
        # Analyze each file and collect structured responses
        for file in self.financial_files:
            analysis_result = self.analyze_file(file)
            print(analysis_result)
            self.analysis.append(analysis_result)
        return self.analysis
