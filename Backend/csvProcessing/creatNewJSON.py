import json
import os


def load_json_data(filepath):
    """Load JSON data from a file."""
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def get_last_part_of_url(url):
    """Extract the last part of the URL after the last slash."""
    if url.endswith("/"):
        url = url[:-1]
    return url.split("/")[-1]


def merge_json_objects(data):
    """Merge JSON objects based on the last part of the URL."""
    merged_data = {}
    for key, value in data.items():
        url = value["Story_URL"]
        last_part = get_last_part_of_url(url)
        if last_part in merged_data:
            # Merging process: prefer non-empty values from either of the entries
            existing = merged_data[last_part]
            for field in value:
                if value[field]:  # Prefer non-empty or more complete info fields
                    existing[field] = value[field]
        else:
            merged_data[last_part] = value
            # Keep a reference to the original key to maintain the "smaller index"
            merged_data[last_part]["original_key"] = key
    # Return the dictionary, reindexed to use the smallest original key
    reindexed_data = {
        val["original_key"]: {k: v for k, v in val.items() if k != "original_key"}
        for val in merged_data.values()
    }
    return reindexed_data


def save_json_data(filepath, data):
    """Save JSON data to a file."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# Path to your JSON file
filepath = "sheetTotal.json"

# Load, process, and save the JSON data
original_data = load_json_data(filepath)
merged_data = merge_json_objects(original_data)
save_json_data("processedDataNew.json", merged_data)

print("Merging complete. Data saved to 'processedData.json'.")
