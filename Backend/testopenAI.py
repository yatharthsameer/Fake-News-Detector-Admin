import json
import csv
import requests
import openai
import re

# Set your OpenAI API key
openai.api_key = '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'

# Function to make a POST request and get the top articles
def get_top_articles(query, number_of_top_articles=3):
    response = requests.post('http://localhost:3001/search', json={'query': query})
    if response.status_code == 200:
        results = response.json()
        return results[:number_of_top_articles]
    return []

# Function to ask ChatGPT to choose the best matching article
def get_best_match_from_chatgpt(claim, articles):
    prompt = f"Read the claim and the summaries of three articles below. Select the article that best matches the claim in essence.\n\nClaim: {claim}\n\nArticles:\n"
    for i, article in enumerate(articles, 1):
        prompt += f"{i}. {article['data']['Headline']} (Match: {article['percentage']}%)\n"
    prompt += "\nWhich article number best matches the claim?"
    print(prompt)
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=60
    )
    
    # Use regex to find the first number in the response, which should be the article number.
    match = re.search(r'\d+', response.choices[0].text)
    if match:
        best_match_index = int(match.group()) - 1
        return articles[best_match_index]['data']['Headline']
    else:
        # If no number is found, we need to handle this case (perhaps ask again, or choose a default)
        return "No clear best match found by ChatGPT."

# Load the rephrased claims from a file (the file should be prepared with the rephrased claims)
with open('testopenAI.json', 'r') as file:
    rephrased_claims = json.load(file)
    print(f"Loaded {len(rephrased_claims)} rephrased claims.")
# Prepare a CSV file to write the results
with open('results_comparison.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the header row
    csvwriter.writerow(['Original Claim', 'Rephrased Claim', 'ChatGPT Selected Article', 'Top Matched Article'])
    print("Processing rephrased claims...")
    # Iterate over the rephrased claims
    for claim_group in rephrased_claims:
        original_claim = claim_group['original']
        for rephrased_claim in claim_group['rephrased']:
            # Get the top 3 articles for the rephrased claim from the server
            top_articles = get_top_articles(rephrased_claim)
            # Get the best match from ChatGPT
            if top_articles:
                best_match_article = get_best_match_from_chatgpt(rephrased_claim, top_articles)
                # Write to CSV
                csvwriter.writerow([original_claim, rephrased_claim, best_match_article, top_articles[0]['data']['Headline']])

print("Completed processing rephrased claims.")
