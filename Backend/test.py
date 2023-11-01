import json
import requests
import csv

# Load the queries from the test.json file
with open('test.json', 'r') as file:
    queries = json.load(file)

# Open a CSV file to write the results
with open('results.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the header row
    csvwriter.writerow(['Query', 'Result 1', 'Percentage 1', 'Result 2', 'Percentage 2', 'Result 3', 'Percentage 3', 'Result 4', 'Percentage 4', 'Result 5', 'Percentage 5'])

    # Iterate over each query
    for query in queries:
        # Make the POST request to the server
        response = requests.post('http://localhost:3001/search', json={'query': query})
        if response.status_code == 200:
            # Parse the response
            data = response.json()
            # Extract the top 5 results
            results = data[:5]
            # Prepare the row to write to the CSV
            row = [query]
            for result in results:
                row.extend([result['data']['Headline'], result['percentage']])
            # Write the row to the CSV file
            csvwriter.writerow(row)
