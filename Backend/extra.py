import json

# Load the JSON data from the file
with open("dataTemp.json", "r") as json_file:
    data = json.load(json_file)

# Read the image links from the text file into a list
with open("image_links_temp.txt", "r") as links_file:
    image_links = [line.strip() for line in links_file]

# Assuming the ordering of objects in the JSON file and their image links in the text file is the same,
# add each image link to its corresponding JSON object
for i, item in enumerate(data):
    if i < len(image_links):
        item["img"] = image_links[i]
    else:
        item["img"] = (
            None  # or you can choose to not add the img key at all if no link is available
        )

# Write the modified data to a new JSON file
# Write the modified data to a new JSON file, ensuring UTF-8 encoding
with open("dataTemp.json", "w", encoding="utf-8") as output_file:
    json.dump(data, output_file, ensure_ascii=False, indent=4)
