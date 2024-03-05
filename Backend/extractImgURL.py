import json
import requests
from bs4 import BeautifulSoup

# Load the JSON data from the file
with open("dataTemp.json", "r") as file:
    data = json.load(file)

# Open the file for writing outside the loop to avoid opening and closing it multiple times
with open("image_links_temp.txt", "a") as file:
    for item in data:
        story_url = item.get("Story_URL")
        if story_url:
            response = requests.get(story_url)
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
