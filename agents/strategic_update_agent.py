from openai import OpenAI

class StrategicUpdatesAgent:
    def __init__(self, strategic_files, api_key):
        self.strategic_files = strategic_files
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
        You are a business strategy expert analyzing the following strategic update document.

        **Document Details**:
        - **Title**: {file_name}
        - **Category**: {file_sub_category}
        - **Publish Date**: {publish_date}
        - **Short Description**: {short_description if short_description else "N/A"}
        - **URL**: {pdf_url}

        **Instructions**:
        1. Summarize the strategic significance of the document (e.g., Acquisition, Joint Venture).
        2. Highlight potential synergies or benefits (e.g., market expansion, operational efficiency).
        3. Identify risks or challenges related to the strategic update.
        4. Provide a forward-looking perspective on how this impacts the company's growth or market position.

        Ensure your response is professional and concise.
        """
        return self.query_openai(prompt)

    def query_openai(self, prompt):
        client = OpenAI(api_key=self.api_key)
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a business strategy expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

    def run(self):
        for file in self.strategic_files:
            summary = self.analyze_file(file)
            self.analysis.append(summary)
        return self.analysis
