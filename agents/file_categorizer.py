class FileCategorizer:
    def __init__(self, files):
        self.files = files

    def categorize_files(self):
        categorized_files = {
            "Financial Analysis": [],
            "Strategic Updates": [],
            "Corp. Actions": [],
            "Organizational Updates": [],
            "Other": []
        }

        # Define subcategory mappings
        financial_analysis_subcategories = [
            "Financial Results", "Limited Review Report", "Auditors Report", 
            "Change in Accounting Year", "Declaration of NAV", 
            "Quarterly AUM Disclosure", "Monthly AUM Disclosure" , "Earnings Call Transcript"
        ]
        strategic_updates_subcategories = [
            "Acquisition", "Joint Venture", "Amalgamation / Merger", "De-merger", 
            "Sale or disposal", "Slump Sale", "Open Offer", "Issue of Securities", 
            "Qualified Institutional Placement", "Preferential Issue", 
            "Investor Presentation", "Press Release / Media Release", 
            "Agreement", "Memorandum of Understanding / Agreements", 
            "Update-Acquisition / Scheme / Sale / Disposal / Reg30", "Newspaper Publication",
            "Restructuring", "Earnings Call Transcript", "Strategic Diversification / Disinvestment"
        ]
        corp_actions_subcategories = [
            "Bonus", "Dividend", "Record Date", "Capital Reduction", 
            "Sub-division / Stock Split", "Bonds / Right issue", 
            "Consolidation of Shares", "Amalgamation / Merger / Demerger", 
            "Book Closure", "Funds raising by issuance of Debt Securities by Large Entities"
        ]
        organizational_updates_subcategories = [
            "New Hiring", "Resignation of Director", "Resignation of Chairman",
            "Resignation of Chairman and Managing Director", "Resignation of Chief Executive Officer (CEO)",
            "Resignation of Chief Financial Officer (CFO)", "Resignation of Managing Director",
            "Resignation of Statutory Auditors", "Resignation of Company Secretary / Compliance Officer",
            "Appointment of Director", "Appointment of Chairman", "Appointment of Chairman and Managing Director",
            "Appointment of Managing Director", "Appointment of Chief Executive Officer (CEO)",
            "Appointment of Chief Financial Officer (CFO)", "Appointment of Managing Director & CEO",
            "Appointment of Company Secretary / Compliance Officer", "Change in Management",
            "Change in Management Control", "Change in Financial Year", "Demise", "Retirement", "Cessation",
            "Change in Registered Office Address", "Change in Corporate Office Address", 
            "Replacement of Interim Resolution Professional (IRP)", "Appointment of Interim Resolution Professional (IRP)",
            "Winding-up", "Impact of Audit Qualifications"
        ]

        # Categorize files
        for file in self.files:
            sub_category = file.get("file_sub_category", "")
            if sub_category in financial_analysis_subcategories:
                categorized_files["Financial Analysis"].append(file)
            elif sub_category in strategic_updates_subcategories:
                categorized_files["Strategic Updates"].append(file)
            elif sub_category in corp_actions_subcategories:
                categorized_files["Corp. Actions"].append(file)
            elif sub_category in organizational_updates_subcategories:
                categorized_files["Organizational Updates"].append(file)
            else:
                categorized_files["Other"].append(file)
        
        return categorized_files
