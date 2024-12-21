import os
from weasyprint import HTML
from agents.html_parser import HTMLParserAgent

def test_html_parser_to_pdf(newsletter_file_path, openai_api_key):
    """
    Test method to validate the functionality of the HTMLParserAgent and generate a PDF output.

    :param newsletter_file_path: Path to the test newsletter text file.
    :param openai_api_key: OpenAI API key for the agent.
    """
    try:
        # Step 1: Check if the file exists
        if not os.path.exists(newsletter_file_path):
            print(f"File not found: {newsletter_file_path}")
            return

        # Step 2: Read the content of the test file
        with open(newsletter_file_path, "r") as file:
            newsletter_content = file.read()

        # Step 3: Initialize the HTMLParserAgent
        html_parser = HTMLParserAgent(api_key=openai_api_key)

        # Step 4: Generate HTML from the newsletter content
        print("Generating HTML from newsletter content...")
        html_content = html_parser.generate_html(newsletter_content)

        # Step 5: Validate HTML generation
        if not html_content:
            print("HTML generation failed. Received empty content.")
            return

        print("HTML generation successful.")

        # Step 6: Convert HTML to PDF using WeasyPrint
        output_dir = "test_outputs"
        os.makedirs(output_dir, exist_ok=True)
        pdf_output_path = os.path.join(output_dir, "test_newsletter.pdf")

        print("Converting HTML to PDF...")
        HTML(string=html_content).write_pdf(pdf_output_path)

        print(f"PDF generated successfully and saved to: {pdf_output_path}")

    except Exception as e:
        print(f"Error during HTML to PDF test: {e}")

# Usage
test_html_parser_to_pdf(
    "/Users/kshitijbanka/finance-newletter/final_newsletters/Conservative_Investor_newsletter.txt",
    os.getenv("OPENAI_API_KEY")
)
