import json


def convert_images_to_list(input_json, output_json):
    with open(input_json, "r", encoding="utf-8") as file:
        data = json.load(file)

    for key, value in data.items():
        # Collect all image links
        img_list = []
        for i in range(1, 11):  # Assuming there can be up to img10
            img_key = f"img{i}" if i > 1 else "img"
            if img_key in value:
                img_list.append(
                    value.pop(img_key)
                )  # Remove the img key from the object and add to list

        if img_list:
            value["img"] = img_list  # Add the list back to the 'img' key

    # Save the updated JSON back to the file
    with open(output_json, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print(f"Conversion complete. The updated JSON is saved to {output_json}")


# Specify the input and output file paths
input_json = "allData.json"
output_json = "updated_allData.json"

# Run the conversion
convert_images_to_list(input_json, output_json)
