# Example usage
from utils.matlab_graph_util import generate_graphs_from_json


json_data = [
    {
        "graph_type": "line_chart",
        "title": "Net Profit Margin Change Over Time",
        "x_axis": {
            "label": "Quarter",
            "data": ["Q1 FY23", "Q2 FY23", "Q3 FY23", "Q4 FY23", "Q1 FY24", "Q2 FY24", "Q3 FY24"]
        },
        "y_axis": {
            "label": "Net Profit Margin (%)",
            "data": ["7.0", "7.5", "7.7", "8.0", "8.3", "8.4", "8.5"]
        },
        "insights": "Highlights improvement in profitability margins over the recent quarters."
    },
    {
        "graph_type": "bar_chart",
        "title": "Capital Expenditure of Reliance Industries",
        "x_axis": {
            "label": "Financial Year",
            "data": ["2020", "2021", "2022", "2023", "2024"]
        },
        "y_axis": {
            "label": "Capital Expenditure (in crore INR)",
            "data": [25000, 27000, 28400, 30102, 30102]
        },
        "insights": "Displays Reliance Industries' investment strategy and capital allocation trends over the years."
    }
]

stock_name = "Reliance Industries"
graph_paths = generate_graphs_from_json(json_data, stock_name)
print(f"Generated graph paths: {graph_paths}")
