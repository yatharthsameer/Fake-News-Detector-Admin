import json
import requests
import csv

# Function to make a POST request and get the top article
def get_top_article(query):
    response = requests.post('http://localhost:3001/search', json={'query': query})
    if response.status_code == 200:
        results = response.json()
        if results and len(results) > 0:
            return results[0]['data']['Headline']
    return None

# Load the queries from the JSON file
with open('test2.json', 'r') as file:
    data = json.load(file)

# Variables to track matches and total for accuracy calculation
total_claims = 0
matched_claims = 0

# Open a CSV file to write the results
with open('results.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the header row
    csvwriter.writerow(['Query', 'Top Matched Article'])

    # Iterate over each claim set
    for claim_set in data['claims']:
        # Process the original claim first
        original_claim = claim_set[0]
        original_top_article = get_top_article(original_claim)
        csvwriter.writerow([original_claim, original_top_article or 'No results found'])

        # Then process each rephrased claim
        for rephrased_claim in claim_set[1:]:
            rephrased_top_article = get_top_article(rephrased_claim)
            csvwriter.writerow([rephrased_claim, rephrased_top_article or 'No results found'])

            # Compare and update the accuracy metrics
            if original_top_article == rephrased_top_article:
                matched_claims += 1
            total_claims += 1

# Calculate the accuracy
accuracy = (matched_claims / total_claims) * 100 if total_claims > 0 else 0
print(f"Accuracy of the model: {accuracy}%")

# Save the accuracy to a JSON file
with open('results.json', 'w') as jsonfile:
    json.dump({'accuracy': accuracy}, jsonfile)
