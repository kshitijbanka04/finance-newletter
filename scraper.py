import requests
from datetime import datetime, timedelta
from supabase import create_client
from typing import List, Dict
import os


class BSEScraper:
    def __init__(self):
        self.base_url = "https://www.bseindia.com/corporates/ann.html"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
        }

    def get_announcements(self, security_code: str, days_back: int = 90) -> List[Dict]:
        """
        Fetch all announcements for a given security code from BSE with pagination
        """
        announcements = []
        api_url = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
        
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://www.bseindia.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.bseindia.com/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }
        
        page = 1
        while True:
            print(f"Searching for page: {page}")
            params = {
                "pageno": page,
                "strCat": -1,
                "strPrevDate": (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d"),
                "strScrip": security_code,
                "strSearch": "P",
                "strToDate": datetime.now().strftime("%Y%m%d"),
                "strType": "C",
                "subcategory": -1
            }

            try:
                response = requests.get(api_url, headers=headers, params=params)
                response.raise_for_status()  # Raise exception for HTTP errors
                data = response.json()
                
                # Check if there are announcements in the response
                if "Table" in data and data["Table"]:
                    for announcement in data["Table"]:
                        # Skip irrelevant announcements
                        if any(keyword in announcement["NEWSSUB"].lower() 
                            for keyword in ["compliances", "duplicate", "intimation"]):
                            continue

                        # Filter by relevant categories
                        elif announcement["CATEGORYNAME"] and announcement["CATEGORYNAME"].lower() in ["company update", "board meeting", "result", "corp. action", "new listing"]:
                            pdf_file_url = ""
                            if(announcement["PDFFLAG"]==1):
                                print("Encountered Attach his")
                                pdf_file_url = f"https://www.bseindia.com/xml-data/corpfiling/AttachHis/{announcement['ATTACHMENTNAME']}"
                            else:
                                print("Encountered Attach Live")
                                pdf_file_url = f"https://www.bseindia.com/xml-data/corpfiling/AttachLive/{announcement['ATTACHMENTNAME']}"
                            
                            announcement_data = {
                                    "file_name": announcement["NEWSSUB"],
                                    "pdf_file_url": pdf_file_url,
                                    "publish_date": announcement["NEWS_DT"],
                                    "file_category": announcement["CATEGORYNAME"],
                                    "file_sub_category": announcement["SUBCATNAME"],
                                    "page_count": announcement["TotalPageCnt"],
                                    "short_description": announcement["MORE"]
                                }
                            announcements.append(announcement_data)
                else:
                    # Exit the loop if no announcements are found on the current page
                    break
                
                # Move to the next page
                page += 1
            
            except Exception as e:
                print(f"Error fetching data for security code {security_code}, page {page}: {str(e)}")
                break  # Exit the loop on error
                
        return announcements


class SupabaseManager:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase = create_client(supabase_url, supabase_key)

    def update_stock_data(self, stock_data: Dict):
        """
        Update stock data in Supabase with new document structure
        """
        try:
            # Check if stock already exists
            result = self.supabase.table('stock_data') \
                .select('*') \
                .eq('stock_symbol', stock_data['stock_symbol']) \
                .execute()

            if len(result.data) > 0:
                # Update existing record
                self.supabase.table('stock_data') \
                    .update({
                        'documents': stock_data['documents']
                    }) \
                    .eq('stock_symbol', stock_data['stock_symbol']) \
                    .execute()
            else:
                # Insert new record
                self.supabase.table('stock_data') \
                    .insert(stock_data) \
                    .execute()

        except Exception as e:
            print(f"Error updating data for stock {stock_data['stock_symbol']}: {str(e)}")


def main():
    # Initialize scraper and Supabase manager
    scraper = BSEScraper()
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # Initialize Supabase client    
    supabase_manager = SupabaseManager(
        supabase_url=SUPABASE_URL,
        supabase_key=SUPABASE_KEY
    )
    
    # Define your stock categories
    stocks = {
        "Conservative": [
            {"name": "Reliance Industries Limited", "code": "500325", "symbol": "RELIANCE", "industry": "Conglomerate"},
            {"name": "HDFC Bank Limited", "code": "500180", "symbol": "HDFCBANK", "industry": "Banking"},
            {"name": "Infosys Limited", "code": "500209", "symbol": "INFY", "industry": "Information Technology"},
            {"name": "Asian Paints Limited", "code": "500820", "symbol": "ASIANPAINT", "industry": "Paints"}
        ],
        "Growth-Oriented": [
            {"name": "Tata Motors Limited", "code": "500570", "symbol": "TATAMOTORS", "industry": "Automotive"},
            {"name": "Adani Enterprises Limited", "code": "512599", "symbol": "ADANIENT", "industry": "Conglomerate"},
            {"name": "Coforge Limited", "code": "532541", "symbol": "COFORGE", "industry": "IT Services"},
            {"name": "Godrej Consumer Products Limited", "code": "532424", "symbol": "GODREJCP", "industry": "FMCG"},
            {"name": "Laurus Labs Limited", "code": "540222", "symbol": "LAURUSLABS", "industry": "Pharmaceuticals"}
        ],
        "Sector-Specific": [
            {"name": "Tech Mahindra Limited", "code": "532755", "symbol": "TECHM", "industry": "IT Services"},
            {"name": "Sun Pharmaceutical Industries Ltd.", "code": "524715", "symbol": "SUNPHARMA", "industry": "Pharmaceuticals"},
            {"name": "Divi's Laboratories Limited", "code": "532488", "symbol": "DIVISLAB", "industry": "Pharmaceuticals"},
            {"name": "Zydus Lifesciences Limited", "code": "532321", "symbol": "ZYDUSLIFE", "industry": "Healthcare"},
            {"name": "L&T Technology Services Limited", "code": "540115", "symbol": "LTTS", "industry": "Engineering R&D"}
        ],
        "Small-Cap": [
            {"name": "Vaibhav Global Limited", "code": "532156", "symbol": "VAIBHAVGBL", "industry": "Retail"},
            {"name": "Chemplast Sanmar Limited", "code": "543336", "symbol": "CHEMPLASTS", "industry": "Specialty Chemicals"},
            {"name": "Route Mobile Limited", "code": "543228", "symbol": "ROUTE", "industry": "IT Services"},
            {"name": "Polycab India Limited", "code": "542652", "symbol": "POLYCAB", "industry": "Electrical Equipment"},
            {"name": "Laxmi Organic Industries Limited", "code": "543277", "symbol": "LXCHEM", "industry": "Chemicals"}
        ],
        "Diversified": [
            {"name": "Hindustan Unilever Limited", "code": "500696", "symbol": "HINDUNILVR", "industry": "FMCG"},
            {"name": "ICICI Bank Limited", "code": "532174", "symbol": "ICICIBANK", "industry": "Banking"},
            {"name": "Bajaj Finance Limited", "code": "500034", "symbol": "BAJFINANCE", "industry": "NBFC"},
            {"name": "Avenue Supermarts Limited", "code": "540376", "symbol": "DMART", "industry": "Retail"},
            {"name": "The Tata Power Company Limited", "code": "500400", "symbol": "TATAPOWER", "industry": "Utilities"}
        ]
    }
    
    for category, stock_list in stocks.items():
        for stock in stock_list:
            # Get announcements
            print(f"Updating for {stock}")
            announcements = scraper.get_announcements(stock["code"])
            
            # Prepare stock data with new structure
            stock_data = {
                "stock_name": stock["name"],
                "stock_symbol": stock["symbol"],
                "stock_code": stock["code"],
                "industry": stock["industry"],
                "category": category,
                "documents": announcements  # Direct array of document objects
            }
            
            # Update Supabase
            supabase_manager.update_stock_data(stock_data)


if __name__ == "__main__":
    main()
