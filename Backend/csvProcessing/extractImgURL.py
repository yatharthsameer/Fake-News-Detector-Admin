import csv
import json
import requests
from bs4 import BeautifulSoup
import time
import os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


def convert_csv_to_json(csv_filename, json_filename):
    json_data = {}
    with open(csv_filename, mode="r", encoding="utf-8") as csvfile:
        csvreader = csv.DictReader(csvfile)
        for i, row in enumerate(csvreader, start=1):  # Start counting from 1
            json_data[i] = {  # Use i as the ID
                "Story_Date": row.get("Story Date"),
                "Story_URL": row.get("Story URL"),
                "Headline": row.get("Headline"),
                "Claim_URL": row.get("Claim URL"),
                "What_(Claim)": row.get("What (Claim)"),
                "About_Subject": row.get("About Subject"),
                "About_Person": row.get("About Person"),
            }

    with open(json_filename, mode="w", encoding="utf-8") as jsonfile:
        json.dump(json_data, jsonfile, ensure_ascii=False, indent=4)

    print(
        f"CSV data has been successfully converted to JSON and saved to {json_filename}"
    )


def fetch_and_log_image_urls(json_file_path, output_txt_file):
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    with open(output_txt_file, "w", encoding="utf-8") as file:
        for id, item in data.items():  # Adjusted iteration
            story_url = item["Story_URL"]  # Directly access since we know the structure
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
                            file.write(
                                f"{id},{image_link}\n"
                            )  # Write ID and image link
                        else:
                            no_image_message = f"No image found for {story_url}"
                            print(no_image_message)
                            file.write(f"{id},\n")  # Write ID and no image
                    else:
                        error_message = f"Failed to fetch {story_url} with status code {response.status_code}"
                        print(error_message)
                        file.write(
                            f"{id},\n"
                        )  # Write ID and no image due to fetch error
                except Exception as e:
                    error_message = f"Error processing {story_url}: {str(e)}"
                    print(error_message)
                    file.write(
                        f"{id},\n"
                    )  # Write ID and no image due to processing error

                time.sleep(1)


def update_json_with_image_links(
    original_json_path, image_links_file, updated_json_path
):
    with open(original_json_path, "r", encoding="utf-8") as file:
        data = json.load(file)  # This should be a dictionary now, with IDs as keys

    # Read image links and associate them with IDs
    with open(image_links_file, "r", encoding="utf-8") as file:
        for line in file:
            id, image_link = line.strip().split(",", 1)  # Split line at first comma
            if (
                id in data and image_link
            ):  # Check if ID exists and image_link is not empty
                data[id]["img"] = image_link  # Assign image link to the correct ID

    # Save the updated data back to JSON
    with open(updated_json_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def extract_img_links(json_path):
    with open(json_path, "r") as file:
        data = json.load(file)
        return [(id, story["img"]) for id, story in data.items() if "img" in story]


def download_images(urls_with_ids, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    for id, url in urls_with_ids:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                file_path = f"{folder}/image_{id}.jpg"
                with open(file_path, "wb") as file:
                    file.write(response.content)
                print(f"Downloaded image for ID {id} to {file_path}")
        except Exception as e:
            print(f"Failed to download image for ID {id} from {url}: {e}")


# Set your paths and folder name
csv_filename = "hindi.csv"

json_file_path = "hindi.json"
output_txt_file = "hindi.txt"
updated_json_path = "hindi.json"
folder_name = "../data"  # Adjust path as needed

# Process sequence
convert_csv_to_json(csv_filename, json_file_path)  # Convert CSV to JSON first
fetch_and_log_image_urls(json_file_path, output_txt_file)
update_json_with_image_links(json_file_path, output_txt_file, updated_json_path)
image_urls = extract_img_links(updated_json_path)
download_images(image_urls, folder_name)
