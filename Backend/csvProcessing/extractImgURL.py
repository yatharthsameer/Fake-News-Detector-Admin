import json
import requests
from bs4 import BeautifulSoup
import time
import os

# Headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


def fetch_and_log_image_urls(json_file_path, output_txt_file):
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    with open(
        output_txt_file, "w", encoding="utf-8"
    ) as file:  # Change "a" to "w" to overwrite existing file
        for item in data:
            story_url = item.get("Story_URL")
            if story_url:
                try:
                    response = requests.get(story_url, headers=headers)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, "html.parser")
                        img_tag = soup.find(
                            "img",
                            class_="attachment-hero-image-single-size size-hero-image-single-size wp-post-image",
                        )
                        if img_tag:
                            image_link = img_tag["src"]
                            print(image_link)
                            file.write(image_link + "\n")
                        else:
                            no_image_message = f"No image found for {story_url}"
                            print(no_image_message)
                            file.write(no_image_message + "\n")
                    else:
                        error_message = f"Failed to fetch {story_url} with status code {response.status_code}"
                        print(error_message)
                        file.write(error_message + "\n")
                except Exception as e:
                    error_message = f"Error processing {story_url}: {str(e)}"
                    print(error_message)
                    file.write(error_message + "\n")

                # Delay to respect the server's load
                time.sleep(1)


def update_json_with_image_links(
    original_json_path, image_links_file, updated_json_path
):
    with open(original_json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    with open(image_links_file, "r", encoding="utf-8") as file:
        image_links = [link.strip() for link in file.readlines()]

    for index, item in enumerate(data):
        if index < len(image_links):
            item["img"] = image_links[index]

    with open(updated_json_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def extract_img_links(json_path):
    with open(json_path, "r") as file:
        data = json.load(file)
        return [story["img"] for story in data if "img" in story]


def download_images(urls, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for i, url in enumerate(urls):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                file_path = f"{folder}/image_{i+1}.jpg"
                with open(file_path, "wb") as file:
                    file.write(response.content)
                print(f"Downloaded image {i+1} to {file_path}")
        except Exception as e:
            print(f"Failed to download image {i+1} from {url}: {e}")


# Set your paths and folder name
json_file_path = "hindi.json"
output_txt_file = "hindi.txt"
updated_json_path = "updated_data.json"
folder_name = "./data"  # Adjust path as needed

# Process sequence
fetch_and_log_image_urls(json_file_path, output_txt_file)
update_json_with_image_links(json_file_path, output_txt_file, updated_json_path)
image_urls = extract_img_links(updated_json_path)
download_images(image_urls, folder_name)
