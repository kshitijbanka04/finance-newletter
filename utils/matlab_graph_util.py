import os
import matplotlib
import matplotlib.pyplot as plt

# Use a non-interactive backend to avoid GUI-related issues
matplotlib.use("Agg")


def generate_graphs_from_json(json_data, stock_name):
    """
    Generate and save graphs from JSON data using matplotlib.

    Parameters:
        json_data (list): List of graph configurations.
        stock_name (str): Name of the stock for organizing the output folder.

    Returns:
        list: Paths of successfully generated graphs.
    """
    # Create the attachments directory if it doesn't exist
    base_output_dir = os.path.join("attachments_final", stock_name.replace(" ", "_"))
    os.makedirs(base_output_dir, exist_ok=True)

    graph_paths = []  # Store paths of successfully generated graphs

    for idx, graph in enumerate(json_data):
        graph_type = graph.get("graph_type")
        title = graph.get("title", f"Graph {idx + 1}")
        x_axis = graph.get("x_axis", {})
        y_axis = graph.get("y_axis", {})
        labels = graph.get("labels", [])
        data = graph.get("data", [])
        
        # Initialize the plot
        plt.figure(figsize=(10, 6))

        try:
            # Check for required data
            if graph_type in ["bar_chart", "line_chart"]:
                x_data = x_axis.get("data", [])
                y_data = y_axis.get("data", [])

                if not x_data or not y_data:
                    raise ValueError(f"Missing data for {graph_type}: {title}")

                # Convert y_data to float
                def convert_to_float(value):
                    if isinstance(value, (int, float)):
                        return float(value)
                    if isinstance(value, str):
                        try:
                            return float(value.replace('%', '').strip())
                        except ValueError:
                            raise ValueError(f"Non-numeric data found in y_axis: {value}")
                    raise ValueError(f"Unsupported type in y_axis: {type(value)}")

                y_data = [convert_to_float(val) for val in y_data]

            # Generate the appropriate graph
            if graph_type == "bar_chart":
                plt.bar(x_data, y_data)
                plt.xlabel(x_axis.get("label", "X-axis"))
                plt.ylabel(y_axis.get("label", "Y-axis"))
                plt.title(title)

            elif graph_type == "line_chart":
                plt.plot(x_data, y_data, marker="o")
                plt.xlabel(x_axis.get("label", "X-axis"))
                plt.ylabel(y_axis.get("label", "Y-axis"))
                plt.title(title)

            elif graph_type == "pie_chart":
                if not data or not labels:
                    raise ValueError(f"Invalid data or labels for pie chart: {title}")

                pie_data = [convert_to_float(val) for val in data]
                plt.pie(pie_data, labels=labels, autopct="%1.1f%%")
                plt.title(title)

            else:
                print(f"Unsupported graph type: {graph_type}")
                continue

            # Save the plot to a file
            output_file = os.path.join(base_output_dir, f"{idx}.png")
            plt.savefig(output_file, bbox_inches="tight")
            graph_paths.append(output_file)  # Append the path of the generated graph
            print(f"Saved graph: {output_file}")

        except Exception as e:
            print(f"Error generating graph {idx + 1}: {e}")

        finally:
            # Close the plot to free memory
            plt.close()

    return graph_paths  # Return paths of successfully generated graphs
