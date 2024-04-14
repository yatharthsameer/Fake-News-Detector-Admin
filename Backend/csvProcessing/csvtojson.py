import json
import csv


def json_to_csv(json_filepath, csv_filepath):
    # Load the JSON data from the file
    with open(json_filepath, "r") as file:
        data = json.load(file)

    # Open the CSV file for writing
    with open(csv_filepath, "w", newline="", encoding="utf-8") as csvfile:
        # Determine the fieldnames from the first item keys if available
        fieldnames = list(data[list(data.keys())[0]].keys()) if data else []

        # Create a CSV DictWriter object using the fieldnames
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Write data rows
        for item in data.values():
            writer.writerow(item)

    print(f"Data successfully written to {csv_filepath}")


# Example usage:
json_filepath = "processedData.json"  # Adjust to your JSON file's path
csv_filepath = "output.csv"  # Desired output CSV file path

json_to_csv(json_filepath, csv_filepath)
