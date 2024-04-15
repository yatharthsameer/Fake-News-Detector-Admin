import csv
import json
import requests
from bs4 import BeautifulSoup
import time
import os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


import csv
import json


def convert_csv_to_json(csv_filename, json_filename):
    json_data = {}
    unique_check = set()  # To store combinations of Headline and Story_Date

    with open(csv_filename, mode="r", encoding="utf-8") as csvfile:
        csvreader = csv.DictReader(csvfile)

        # Adjust the enumeration if you need a specific starting index, otherwise, you can start from 1
        for i, row in enumerate(csvreader, start=1):
            # Generate a unique identifier by combining Headline and Story_Date
            # unique_id = f"{row.get('Story_URL')}_{row.get('Story_Date')}"

            # Check if this unique combination is already in the set
            # if unique_id not in unique_check:
            #     unique_check.add(unique_id)  # Add the unique combination to the set
            json_data[i] = {
                "Story_Date": row.get("Story_Date"),
                "Story_URL": row.get("Story_URL"),
                "Headline": row.get("Headline"),
                "Claim_URL": row.get("Claim_URL"),
                "What_(Claim)": row.get("What_(Claim)"),
                "About_Subject": row.get("About_Subject"),
                "About_Person": row.get("About_Person"),
                "img": row.get("img"),
                "tags": row.get("tags"),
            }
            # else:
            #     print(
            #         f"Duplicate entry found and discarded based on Headline and Story_Date: {unique_id}"
            #     )

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
    # Ensure the target folder exists
    if not os.path.exists(folder):
        os.makedirs(folder)

    for id, url in urls_with_ids:
        if url == "NA" or not url:  # Skip entries with no valid image URL
            print(f"Skipping download for ID {id}: No valid URL provided.")
            continue

        try:
            response = requests.get(url)
            if response.status_code == 200:
                file_path = f"{folder}/image_{id}.jpg"
                with open(file_path, "wb") as file:
                    file.write(response.content)
                print(f"Downloaded image for ID {id} to {file_path}")
            else:
                print(
                    f"Failed to download image for ID {id} from {url}: Status code {response.status_code}"
                )
        except Exception as e:
            print(f"Failed to download image for ID {id} from {url}: {e}")


def reindex_json_file(json_filepath):
    # Load the existing data
    with open(json_filepath, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Create a new dictionary with consecutive indices starting from 1
    new_data = {}
    new_index = 1
    for key in sorted(data.keys(), key=int):  # Ensure the keys are sorted numerically
        new_data[str(new_index)] = data[key]
        new_index += 1

    # Save the newly indexed data back to the same JSON file
    with open(json_filepath, "w", encoding="utf-8") as file:
        json.dump(new_data, file, ensure_ascii=False, indent=4)

    print(f"Data has been reindexed and saved back to {json_filepath}")


def fetch_missing_image_urls(json_file_path, output_txt_file):
    # Load existing data
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Determine the last ID processed
    last_id_processed = None
    if os.path.exists(output_txt_file):
        with open(output_txt_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
            if lines:
                last_id_processed = lines[-1].split(",")[0]

    # Iterate through each item in the JSON data
    for id in sorted(
        data.keys(), key=int
    ):  # Ensure numerical order based on string keys
        if last_id_processed is None or int(id) > int(last_id_processed):
            item = data[id]
            if not item.get("img"):  # Check if 'img' field is empty
                print(f"Processing ID {id}",item.get("img"))
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
                            if img_tag and img_tag.get("src"):
                                image_link = img_tag["src"]
                                item["img"] = image_link  # Update JSON directly
                                log_message = f"{id},{image_link}\n"
                            else:
                                item["img"] = "NA"
                                log_message = f"{id},No image found\n"
                        else:
                            item["img"] = "NA"
                            log_message = f"{id},Fetch failed: {response.status_code}\n"
                    except Exception as e:
                        item["img"] = "NA"
                        log_message = f"{id},Error: {e}\n"
                    # Write to log and save JSON incrementally
                    with open(output_txt_file, "a", encoding="utf-8") as log_file:
                        log_file.write(log_message)
                    with open(json_file_path, "w", encoding="utf-8") as json_file:
                        json.dump(data, json_file, ensure_ascii=False, indent=4)
                    time.sleep(1)  # Throttle requests
                else:
                    item["img"] = "NA"
                    with open(output_txt_file, "a", encoding="utf-8") as log_file:
                        log_file.write(f"{id},No Story URL\n")

    print(f"Updated image URLs and saved to {json_file_path}")


# Set your paths and folder name
csv_filename = "allData.csv"

json_file_path = "allData.json"
output_txt_file = "allData.txt"
updated_json_path = "allData.json"
folder_name = "../data"  # Adjust path as needed

# Process sequence
# convert_csv_to_json(csv_filename, json_file_path)  # Convert CSV to JSON first
# fetch_and_log_image_urls(json_file_path, output_txt_file)
# update_json_with_image_links(json_file_path, output_txt_file, updated_json_path)
image_urls = extract_img_links(updated_json_path)
download_images(image_urls, folder_name)
# json_file_path = "mdpFinal.json"
# output_txt_file = "mdpFinal.txt"
# reindex_json_file(json_file_path)

# fetch_missing_image_urls(json_file_path, output_txt_file)
