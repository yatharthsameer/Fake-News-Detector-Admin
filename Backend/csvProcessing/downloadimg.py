import json
import requests
import os
from PIL import Image
from io import BytesIO

# Headers for web requests
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


# Function to extract image links from the JSON file
def extract_img_links(json_path):
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        image_links = []
        for index, story in data.items():
            if isinstance(story.get("img"), list):  # Check if 'img' is a list
                for img_count, img_url in enumerate(story["img"], start=1):
                    if (
                        img_url != "NA" and img_url
                    ):  # Ensure the URL is not 'NA' or empty
                        image_links.append((index, img_count, img_url))
        return image_links


# Function to download images and name them based on the index and image number
def download_images(urls_with_ids, folder):
    # Ensure the target folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    for index, img_number, url in urls_with_ids:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                # Convert and save the image if it's in PNG format
                image = Image.open(BytesIO(response.content))
                if image.format == "PNG":
                    image = image.convert("RGB")  # Convert PNG to JPG (RGB mode)
                    file_path = f"{folder}/image_{index}_{img_number}.jpg"
                    image.save(file_path, "JPEG")
                else:
                    file_path = f"{folder}/image_{index}_{img_number}.jpg"
                    with open(file_path, "wb") as file:
                        file.write(response.content)
                print(f"Downloaded image for index {index} as {file_path}")
            else:
                print(
                    f"Failed to download image for index {index} from {url}: Status code {response.status_code}"
                )
        except Exception as e:
            print(f"Failed to download image for index {index} from {url}: {e}")


# Set your paths and folder name
updated_json_path = "allData.json"
folder_name = "../data"  # Adjust path as needed

# Extract image URLs from the updated JSON file
image_urls = extract_img_links(updated_json_path)

# Download the images
download_images(image_urls, folder_name)
