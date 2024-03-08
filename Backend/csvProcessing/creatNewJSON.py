import json

# Step 1: Load the original JSON data
with open("data.json", "r") as file:
    data = json.load(file)

# Step 2: Read the image links from the text file
with open("image_links.txt", "r") as file:
    image_links = file.readlines()
    # Remove any newline characters from each image link
    image_links = [link.strip() for link in image_links]

# Step 3: Add the image links to the respective JSON objects
for index, item in enumerate(data):
    if index < len(image_links):
        # Add the 'img' key with the corresponding image link
        item["img"] = image_links[index]
    else:
        # If there are no more image links, break the loop
        break

# Step 4: Save the modified data to a new JSON file
with open("updated_data.json", "w") as file:
    json.dump(data, file, indent=4)
