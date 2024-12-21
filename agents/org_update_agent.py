from openai import OpenAI

class OrganizationalUpdatesAgent:
    def __init__(self, org_update_files, api_key):
        self.org_update_files = org_update_files
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
        You are an HR and organizational expert analyzing the following update.

        **Document Details**:
        - **Title**: {file_name}
        - **Category**: {file_sub_category}
        - **Publish Date**: {publish_date}
        - **Short Description**: {short_description if short_description else "N/A"}
        - **URL**: {pdf_url}

        **Instructions**:
        1. Summarize the nature of the organizational update (e.g., Resignation, Appointment, Retirement).
        2. Discuss the potential impact on the company’s operations, management, or stakeholders.
        3. Highlight any notable details (e.g., key accomplishments of the individual, succession plans).
        4. Provide recommendations for stakeholders regarding this update.

        Ensure your response is concise and suitable for stakeholders.
        """
        return self.query_openai(prompt)

    def query_openai(self, prompt):
        # Connect to OpenAI API
        client = OpenAI(api_key=self.api_key)
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an HR and organizational expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

    def run(self):
        for file in self.org_update_files:
            summary = self.analyze_file(file)
            self.analysis.append(summary)
        return self.analysis
