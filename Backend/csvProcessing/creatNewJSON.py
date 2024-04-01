import json

# Read the data from 'allData.json'
with open("allData.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Reindex the objects with consecutive numbers
reindexed_data = {str(i + 1): value for i, value in enumerate(data.values())}

# Write the reindexed data to a new file
with open("reindexedData.json", "w", encoding="utf-8") as new_file:
    json.dump(reindexed_data, new_file, ensure_ascii=False, indent=4)

print("Data has been reindexed and saved to 'reindexedData.json'.")
