from openai import OpenAI
import json

from agents.news_agent import NewsAgent

class StockVisualizer:
    def __init__(self, api_key, tavily_api_key):
        self.api_key = api_key
        self.tavily_api_key = tavily_api_key

    def query_openai(self, prompt):
        """
        Sends a prompt to the OpenAI Completions API and returns the response.
        """
        client = OpenAI(api_key=self.api_key)
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI that generates graph configurations based on data."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

    def analyze_data_with_llm(self, text_data):
        """
        Sends text data to the LLM to determine graph suggestions and fetch missing data.
        """
        # Initial analysis prompt
        prompt = f"""
Analyze the following text data to determine if it contains sufficient information to generate graphs. For each graph, provide the following details in a structured JSON format:

- `graph_type`: Specify the type of graph (e.g., bar_chart, line_chart, pie_chart).
- `title`: A descriptive title for the graph.
- `total_data_needed`: A list of all required data points to create the graph.
- `data_available_from_kb`: An object where keys match the data points from `total_data_needed` or those that will be plotted on the `x-axis` and `y-axis`. Include the specific information available in the text. If a data point is partially available, mention the available portion explicitly.
- `data_needed_from_web`: A list of data points still needed to complete the graph.
- `x_axis`: Define the data to be used for the `x-axis` (for bar and line charts).
- `y_axis`: Define the data to be used for the `y-axis` (for bar and line charts).
- `insights`: A brief insight or takeaway that the graph is expected to highlight.

### JSON Output Format:
[
  {{
    "graph_type": "type_of_graph",
    "title": "title_of_graph",
    "total_data_needed": ["list_of_all_datapoints_required"],
    "data_available_from_kb": {{
      "data_key_1": "value_or_object_with_available_details",
      "data_key_2": "value_or_object_with_available_details"
    }},
    "data_needed_from_web": ["list_of_data_points_still_needed"],
    "x_axis": "x_axis_data_key_or_description",
    "y_axis": "y_axis_data_key_or_description",
    "insights": "brief_insight_about_the_graph"
  }}
]

**Text Data:**
{text_data}
"""

        # Query OpenAI API
        response = self.query_openai(prompt)

        try:
            suggestions = json.loads(response)
            if isinstance(suggestions, list):
                return {"data_available": True, "suggestions": suggestions}
            else:
                return {"data_available": False, "message": response}
        except json.JSONDecodeError:
            return {"data_available": False, "message": response}

    def fetch_data_from_tavily(self, data_needed, stock_name):
        """
        Fetches relevant data points using the Tavily API.
        """
        fetched_data = {}
        for data_point in data_needed:
            news_agent = NewsAgent(stock_name, "", self.tavily_api_key)
            context = news_agent.fetch_from_tavily(query=f"Fetch the data point '{data_point}' for the stock {stock_name}, you can find the data easily on sites like economic times, Screener.")
            if context:
                fetched_data[data_point] = context
        return fetched_data

    import json

    def generate_final_config(self, text_data, stock_name):
        """
        Combines available data with fetched data and queries the LLM for the final graph configuration.
        """
        analysis = self.analyze_data_with_llm(text_data)

        if not analysis["data_available"]:
            raw_message = analysis["message"]
            if raw_message.startswith("```json") and raw_message.endswith("```"):
                json_string = raw_message[7:-3].strip()
            else:
                print("Unexpected format in 'message':", raw_message)
                return []

            try:
                suggestions = json.loads(json_string)
                print("Suggestions are \n", suggestions)
            except json.JSONDecodeError as e:
                print("Error parsing JSON from 'message':", e)
                return []
        else:
            suggestions = analysis["suggestions"]

        final_suggestions = []
        for suggestion in suggestions:
            print("Processing suggestion:", suggestion)

            # Fetch missing data
            data_needed = suggestion.get("data_needed_from_web", [])
            fetch_data = self.fetch_data_from_tavily(data_needed, stock_name)

            suggestion["fetched_data_sources"] = fetch_data

            if data_needed:
                fetched_data = self.fetch_data_from_tavily(data_needed, stock_name)
                print("\n\n\n")
                suggestion["fetched_data_sources"] = fetched_data
            # Combine available and fetched data

            suggestion.pop("data_needed_from_web", None) 
            # Create a prompt for the final graph configuration
            final_prompt = f"""
Based on the following data, generate the final graph configuration for visualization. 

1. Scrape data from the suggestion : fetched_data_sources links if there any to fill the missing data points accurately for the graphs. 
2. Minimize the presence of N/A, null, or empty values by thoroughly validating and cross-referencing the data.
3. For line and bar charts, use the fetched data URLs to provide additional data points for a complete timeline.
4. For pie charts, derive the labels and data values based on the title and fetched data sources.

Your task is to generate the final graph config for the input suggestion, the reason for calling llm here is just that we might have some additional data that needed to be added and given back the graph. 
Please adhere to only giving back json responses. We do not need any introductory message about the graph config.
ALso ensure if you giving monetary values including T for a trillion and B for a Billion we can add this data in the axis description and have just numbers on x and y or pie chart to plot a good graph.
Also for y-axis data do not have commas in the values as dta is a list which already is comma seperated so please DONT do something like
"data": [15,000, 16,134, 17,394, 18,000, 18,500, 17,000, 19,641]

Graph Details:
{json.dumps(suggestion)}

### Output JSON Format for Line/Bar Chart:
```json
{{
  "graph_type": "line_chart", 
  "title": "Chart Title",
  "x_axis": {{
    "label": "X-axis Label",
    "data": ["X-axis Value 1", "X-axis Value 2", "..."]
  }},
  "y_axis": {{
    "label": "Y-axis Label",
    "data": ["Y-axis Value 1", "Y-axis Value 2", "..."]
  }},
  "additional_data": {{
    "key_name": ["value1", "value2", "..."]
  }},
  "insights": "Brief insight about the graph."
}}

###Output JSON Format for Pie Chart:
```json
{{
  "graph_type": "pie_chart",
  "title": "Chart Title",
  "labels": ["Label 1", "Label 2", "..."],
  "data": ["Value1", "Value2", "..."],
  "insights": "Brief insight about the graph."
}}
"""
            final_response = self.query_openai(final_prompt)
            print(f"final_response for suggestion: {final_response}")
            try:
                if final_response.startswith("```json") and final_response.endswith("```"):
                    json_string = final_response[7:-3].strip()
                    print(f"Got the graph config details for json_string: {json_string}")
                    final_suggestion = json.loads(json_string)
                    final_suggestions.append(final_suggestion)
            
            except json.JSONDecodeError:
                final_suggestions.append({"error": "Failed to parse graph configuration from LLM."})

        return final_suggestions
