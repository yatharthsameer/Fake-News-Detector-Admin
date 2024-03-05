import csv
import json

# Define the input CSV file and output JSON file names
csv_filename = "part2.csv"
json_filename = "outputPart2.json"

# Initialize an empty list to hold the processed records
json_data = []

# Open the CSV file for reading
with open(csv_filename, mode="r", encoding="utf-8") as csvfile:
    # Create a CSV reader object
    csvreader = csv.DictReader(csvfile)

    # Process each row in the CSV file
    for row in csvreader:
        # Convert the row to the desired JSON structure
        processed_row = {
            "Story_Date": row.get("Story Date"),
            "Story_URL": row.get("Story URL"),
            "Headline": row.get("Headline"),
            "Claim_URL": row.get("Claim URL"),
            "What_(Claim)": row.get("What (Claim)"),
            "About_Subject": row.get("About Subject"),
            "About_Person": row.get("About Person"),
        }
        # Add the processed row to the list
        json_data.append(processed_row)

# Open the JSON file for writing
with open(json_filename, mode="w", encoding="utf-8") as jsonfile:
    # Write the list of processed records to the JSON file
    json.dump(json_data, jsonfile, ensure_ascii=False, indent=4)

print(f"CSV data has been successfully converted to JSON and saved to {json_filename}")
