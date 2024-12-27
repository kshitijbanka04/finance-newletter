import os
import requests

def upload_to_imgur(image_path, client_id):
    """
    Uploads an image to Imgur and returns the public URL.

    Parameters:
        image_path (str): Path to the image file.
        client_id (str): Imgur API client ID.

    Returns:
        str: Public URL of the uploaded image.
    """
    url = "https://api.imgur.com/3/image"
    headers = {"Authorization": f"Client-ID {client_id}"}
    with open(image_path, "rb") as image_file:
        files = {"image": image_file}
        response = requests.post(url, headers=headers, files=files)

    if response.status_code == 200:
        return response.json()["data"]["link"]
    else:
        print(f"Error uploading to Imgur: {response.json()}")
        return None

def upload_graphs_to_imgur(graph_paths, client_id):
    """
    Upload all graph images to Imgur and return their public URLs.

    Parameters:
        graph_paths (list): List of graph file paths.
        client_id (str): Imgur client ID.

    Returns:
        dict: Mapping of graph filenames to public URLs.
    """
    urls = {}
    for graph_path in graph_paths:
        url = upload_to_imgur(graph_path, client_id)
        if url:
            urls[os.path.basename(graph_path)] = url
    return urls