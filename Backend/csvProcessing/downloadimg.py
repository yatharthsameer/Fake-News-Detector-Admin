import requests
import json

# Assuming the data.json file is stored in a specific path
data_json_path = "./dataReal7k.json"


# Function to extract image URLs from the JSON file
def extract_img_links(json_path):
    with open(json_path, "r") as file:
        data = json.load(file)
        return [story["img"] for story in data if "img" in story]


# Extracting image URLs from the provided JSON file
image_urls = extract_img_links(data_json_path)


# Folder name where the images will be saved
folder_name = "data7k"


# Function to download and save images
def download_images(urls, folder):
    for i, url in enumerate(urls):
        response = requests.get(url)
        if response.status_code == 200:
            file_path = f"{folder}/image_{i+1}.jpg"
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Downloaded image {i+1} to {file_path}")


# Download the images
download_images(image_urls, folder_name)
