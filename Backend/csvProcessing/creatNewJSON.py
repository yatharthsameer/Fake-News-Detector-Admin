import json


def load_json_data(filepath):
    with open(filepath, "r") as file:
        data = json.load(file)
    return data


def merge_json_objects(data):
    merged_data = {}
    for key, value in data.items():
        url = value["Story_URL"]
        if url in merged_data:
            # Merging process: prefer non-empty values from either of the entries
            existing = merged_data[url]
            for field in value:
                if value[field]:  # Prefer non-empty or more complete info fields
                    existing[field] = value[field]
        else:
            merged_data[url] = value
            # Keep a reference to the original key to maintain the "smaller index"
            merged_data[url]["original_key"] = key
    # Return the dictionary, reindexed to use the smallest original key
    reindexed_data = {
        val["original_key"]: {k: v for k, v in val.items() if k != "original_key"}
        for val in merged_data.values()
    }
    return reindexed_data


def save_json_data(filepath, data):
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


# Path to your JSON file
filepath = "sheetTotal.json"

# Load, process, and save the JSON data
original_data = load_json_data(filepath)
merged_data = merge_json_objects(original_data)
save_json_data("processedData.json", merged_data)

print("Merging complete. Data saved to 'processedData.json'.")
