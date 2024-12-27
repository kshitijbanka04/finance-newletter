import os
from openai import OpenAI

class HTMLParserAgent:
    """
    An agent to convert plain text into a visually appealing HTML representation using OpenAI's GPT models.
    """
    def __init__(self, api_key):
        self.api_key = api_key

    def generate_html(self, text_content, graph_urls):
        """
        Converts text content into an HTML representation with graphs.

        Parameters:
        - text_content (str): The plain text content to convert.
        - graph_urls (dict): A dictionary of graph titles and their public URLs.

        Returns:
        - str: Generated HTML content.
        """
        # Prepare the graph references
        graph_content = "\n".join([
            f"### {os.path.splitext(title)[0].replace('_', ' ')}\n![Graph]({url})"
            for title, url in graph_urls.items()
        ])

        prompt = f"""
        NOTE: Do not summarize the text or skip business numbers wherever present.

        You are an HTML designer. Convert the following plain text into a visually appealing HTML document. 
        Use proper headings, subheadings, bullet points, and make the content easy to read. 
        Add a basic inline CSS style to make it look clean and professional. Use appropriate semantic HTML tags. 
        Ensure links in the text are converted into clickable anchors.

        Add the following graphs in their relevant sections:
        {graph_content}

        Here is the content:
        {text_content}
        """

        client = OpenAI(api_key=self.api_key)
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a skilled HTML designer."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"Error generating HTML: {e}")
            return None
