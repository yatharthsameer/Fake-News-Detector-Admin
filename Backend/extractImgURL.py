import json
import requests
from bs4 import BeautifulSoup

# Load the JSON data from the file
with open("data.json", "r") as file:
    data = json.load(file)

image_links = []

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
            image_links.append(image_link)
        else:
            image_links.append(f"No image found for {story_url}")

# Save the image links to a text file
with open("image_links.txt", "w") as file:
    for link in image_links:
        file.write(link + "\n")
