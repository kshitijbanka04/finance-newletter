import os
import json
from concurrent.futures import ThreadPoolExecutor
from agents.file_categorizer import FileCategorizer
from agents.html_parser import HTMLParserAgent
from agents.supervisor_agent import SupervisorAgent
from agents.newsletter_agent import NewsletterAgent
from supabase import create_client
from weasyprint import HTML

from agents.visualizer_agent import StockVisualizer
from utils.matlab_graph_util import generate_graphs_from_json
from utils.upload_to_imgur import upload_graphs_to_imgur

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# API keys for agents
API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "tavily": os.getenv("TAVILY_API_KEY"),
    "exa": os.getenv("EXA_API_KEY"),
    "fallback": os.getenv("NEWS_API_KEY"),
    "imgur": os.getenv("IMGUR_CLIENT_ID")
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


def convert_text_to_html_and_pdf(user_name, text_file_path, graph_paths, client_id):
    """
    Converts a text file to an HTML and then to a PDF with embedded graphs.
    """
    print(f"Converting text file to HTML and PDF for {user_name}...")
    try:
        # Read the text file
        with open(text_file_path, "r") as file:
            text_content = file.read()

        # Upload graphs to Imgur and get their public URLs
        graph_urls = upload_graphs_to_imgur(graph_paths, client_id)

        # Use the HTMLParserAgent to create visually appealing HTML with graphs
        html_parser = HTMLParserAgent(API_KEYS["openai"])
        html_content = html_parser.generate_html(text_content, graph_urls)

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
    Processes a single stock: fetches documents, categorizes them, runs the SupervisorAgent, 
    and generates graph configurations using the Graph Agent.
    """
    print(f"Processing stock: {stock_name}...")

    # Fetch documents
    documents = fetch_stock_documents_supabase(stock_name, stock_code)
    if not documents:
        print(f"No documents to process for {stock_name}")
        return []

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

    # Initialize and use the Graph Agent
    try:
        print(f"Generating graphs for {stock_name}...")
        with open(output_path, "r") as file:
            text_data = file.read()

        graph_agent = StockVisualizer(api_key=API_KEYS["openai"], tavily_api_key=API_KEYS["tavily"])
        graph_configs = graph_agent.generate_final_config(text_data, stock_name)

        if graph_configs:
            return generate_graphs_from_json(graph_configs, stock_name)
        else:
            print(f"No graph data available for {stock_name}")
            return []

    except Exception as e:
        print(f"Error generating graphs for {stock_name}: {e}")
        return []



def generate_final_newsletter(user_profile, graph_paths):
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
    pdf_file_path = convert_text_to_html_and_pdf(user_profile["user_name"], output_path, graph_paths, API_KEYS["imgur"])
    if pdf_file_path:
        print(f"Final newsletter saved as PDF at: {pdf_file_path}")



def process_user_portfolio(user_profile):
    """
    Processes all stocks in a user's portfolio in parallel and generates a newsletter.
    """
    print(f"Processing portfolio for {user_profile['user_name']}...")
    stocks = user_profile["portfolio"]["stocks"]
    all_graph_paths = []  # To collect graph paths for all stocks

    # Use ThreadPoolExecutor to process stocks in parallel
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(process_stock, stock["name"], stock["stock_code"], stock["sector"]): stock["name"]
            for stock in stocks
        }
        for future in futures:
            try:
                stock_graph_paths = future.result()  # Collect graph paths from `process_stock`
                if stock_graph_paths:
                    all_graph_paths.extend(stock_graph_paths)
            except Exception as e:
                print(f"Error processing stock {futures[future]}: {e}")

    # Generate the newsletter, passing all collected graph paths
    generate_final_newsletter(user_profile, all_graph_paths)



if __name__ == "__main__":
    # Example user profile
    user_profile = {
        "user_name": "Conservative Investor",
        "user_age": 45,
        "user_email": "conservative_investor@example.com",
        "portfolio_risk": "Low",
        "portfolio": {
            "stocks": [
                {"name": "Reliance Industries Ltd.", "sector": "Energy", "stock_code": "500325", "market_cap": "LARGE_CAP"},
                {"name": "HDFC Bank", "sector": "Banking", "stock_code": "500180", "market_cap": "LARGE_CAP"},
                {"name": "Infosys", "sector": "IT", "stock_code": "500209", "market_cap": "LARGE_CAP"},
                {"name": "Asian Paints", "sector": "FMCG", "stock_code": "500820", "market_cap": "LARGE_CAP"}
            ],
            "mutual_funds": [
                {"name": "HDFC Balanced Advantage Fund", "type": "Hybrid", "focus": "BALANCED_RISK"},
                {"name": "ICICI Prudential Bluechip Fund", "type": "Equity", "focus": "LARGE_CAP"}
            ]
        }
    }

    process_user_portfolio(user_profile)
