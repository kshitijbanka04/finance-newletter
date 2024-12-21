from openai import OpenAI

class HTMLParserAgent:
    """
    An agent to convert plain text into a visually appealing HTML representation using OpenAI's GPT models.
    """
    def __init__(self, api_key):
        self.api_key = api_key

    def generate_html(self, text_content):
        """
        Converts text content into an HTML representation.

        Parameters:
        - text_content (str): The plain text content to convert.

        Returns:
        - str: Generated HTML content.
        """
        prompt = f"""

        NOTE: Do not summarize the text or do not skip business numbers wherever present.
        
        You are an HTML designer. Convert the following plain text into a visually appealing HTML document. 
        Use proper headings, subheadings, bullet points, and make the content easy to read. 
        Add a basic inline CSS style to make it look clean and professional. Use appropriate semantic HTML tags. 
        Ensure links in the text are converted into clickable anchors.
        Add graphics whereverer possible based on the data presented.

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
