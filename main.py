import os
import json
from concurrent.futures import ThreadPoolExecutor
from agents.file_categorizer import FileCategorizer
from agents.html_parser import HTMLParserAgent
from agents.supervisor_agent import SupervisorAgent
from agents.newsletter_agent import NewsletterAgent
from supabase import create_client
from weasyprint import HTML

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# API keys for agents
API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "tavily": os.getenv("TAVILY_API_KEY"),
    "exa": os.getenv("EXA_API_KEY"),
    "fallback": os.getenv("NEWS_API_KEY"),
}

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_stock_documents_supabase(stock_name, stock_code):
    """
    Fetches documents for a given stock from Supabase.
    """
    try:
        response = supabase.table("stock_data").select("documents").eq("stock_code", stock_code).execute()
        if response.data:
            return response.data[0]["documents"]
        else:
            raise ValueError(f"No documents found for stock: {stock_name}")
    except Exception as e:
        print(f"Error fetching documents for stock {stock_name} from Supabase: {e}")
        return None

def convert_text_to_html_and_pdf(user_name, text_file_path):
    """
    Converts a text file to an HTML and then to a PDF.
    """
    print(f"Converting text file to HTML and PDF for {user_name}...")
    try:
        # Read the text file
        with open(text_file_path, "r") as file:
            text_content = file.read()

        # Use the HTMLParserAgent to create visually appealing HTML
        html_parser = HTMLParserAgent(API_KEYS["openai"])
        html_content = html_parser.generate_html(text_content)

        # Save the HTML content to a file
        output_dir = "final_html_reports"
        os.makedirs(output_dir, exist_ok=True)
        html_file_path = os.path.join(output_dir, f"{user_name.replace(' ', '_')}.html")

        with open(html_file_path, "w") as html_file:
            html_file.write(html_content)

        print(f"HTML file saved at: {html_file_path}")

        # Convert HTML to PDF
        pdf_file_path = os.path.join(output_dir, f"{user_name.replace(' ', '_')}.pdf")
        HTML(html_file_path).write_pdf(pdf_file_path)

        print(f"PDF file saved at: {pdf_file_path}")
        return pdf_file_path

    except Exception as e:
        print(f"Error converting text to HTML and PDF: {e}")
        return None

def process_stock(stock_name, stock_code, sector_name):
    """
    Processes a single stock: fetches documents, categorizes them, and runs the SupervisorAgent.
    """
    print(f"Processing stock: {stock_name}...")

    # Fetch documents
    documents = fetch_stock_documents_supabase(stock_name, stock_code)
    if not documents:
        print(f"No documents to process for {stock_name}")
        return

    # Categorize files
    file_categorizer = FileCategorizer(documents)
    categorized_files = file_categorizer.categorize_files()

    # Run SupervisorAgent
    supervisor_agent = SupervisorAgent(categorized_files, stock_name, sector_name, API_KEYS)
    results = supervisor_agent.run()

    # Save results to a text file
    output_dir = "stock_reports"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{stock_name.replace(' ', '_')}.txt")

    with open(output_path, "w") as file:
        file.write(f"Stock Name: {stock_name}\n")
        file.write(f"Sector: {sector_name}\n")
        file.write("\n=== Analysis Results ===\n")
        for agent, result in results.items():
            file.write(f"\n--- {agent.upper()} ---\n")
            file.write(f"{result}\n")

    print(f"Report saved for {stock_name} at {output_path}")


def generate_final_newsletter(user_profile):
    """
    Generates a newsletter for the entire user portfolio.
    """
    print(f"Generating newsletter for {user_profile['user_name']}...")

    stock_reports_dir = "stock_reports"
    stock_data_files = {}

    # Read all stock text files
    for stock in user_profile["portfolio"]["stocks"]:
        stock_file = os.path.join(stock_reports_dir, f"{stock['name'].replace(' ', '_')}.txt")
        if os.path.exists(stock_file):
            with open(stock_file, "r") as file:
                stock_data_files[stock["name"]] = file.read()
        else:
            print(f"Warning: Report not found for {stock['name']}.")

    if not stock_data_files:
        print("No stock data files available to generate the newsletter.")
        return

    # Run NewsletterAgent
    newsletter_agent = NewsletterAgent(stock_data_files, API_KEYS["openai"])
    final_newsletter = newsletter_agent.generate_newsletter()

    # Save the final newsletter
    output_dir = "final_newsletters"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{user_profile['user_name'].replace(' ', '_')}_newsletter.txt")

    with open(output_path, "w") as file:
        file.write(f"### Personalized Newsletter for {user_profile['user_name']}\n\n")
        file.write(final_newsletter)

    print(f"Final newsletter saved at: {output_path}")

    # Convert the text file to an HTML and PDF
    pdf_file_path = convert_text_to_html_and_pdf(user_profile["user_name"], output_path)
    if pdf_file_path:
        print(f"Final newsletter saved as PDF at: {pdf_file_path}")


def process_user_portfolio(user_profile):
    """
    Processes all stocks in a user's portfolio in parallel and generates a newsletter.
    """
    print(f"Processing portfolio for {user_profile['user_name']}...")
    stocks = user_profile["portfolio"]["stocks"]

    # Use ThreadPoolExecutor to process stocks in parallel
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(process_stock, stock["name"], stock["stock_code"], stock["sector"]) for stock in stocks
        ]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Error processing stock: {e}")

    # Generate the newsletter
    generate_final_newsletter(user_profile)


if __name__ == "__main__":
    # Example user profile
    user_profile = {
        "user_name": "Diversified Investor",
        "user_age": 35,
        "user_email": "diversified_investor@example.com",
        "portfolio_risk": "Medium",
        "portfolio": {
            "stocks": [
                {"name": "Hindustan Unilever", "sector": "FMCG","stock_code": "500696", "market_cap": "LARGE_CAP"},
                {"name": "ICICI Bank", "sector": "Banking","stock_code": "532174", "market_cap": "LARGE_CAP"},
                {"name": "Bajaj Finance", "sector": "NBFC","stock_code": "500034", "market_cap": "LARGE_CAP"},
                {"name": "Avenue Supermarts (DMart)", "sector": "Retail","stock_code": "540376", "market_cap": "MID_CAP"},
                {"name": "Tata Power", "sector": "Utilities","stock_code": "500400", "market_cap": "MID_CAP"}
            ],
            "mutual_funds": [
                {"name": "Kotak Standard Multicap Fund", "type": "Equity", "focus": "MULTICAP"},
                {"name": "Aditya Birla Sun Life Equity Hybrid 95 Fund", "type": "Hybrid", "focus": "BALANCED_RISK"}
            ]
        }
    }

    process_user_portfolio(user_profile)