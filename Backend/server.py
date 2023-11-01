from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import nltk
from nltk.corpus import stopwords

# Define a function to load stopwords from a local file
def load_stopwords(path):
    with open(path, 'r') as file:
        stopwords = file.read().splitlines()
    return set(stopwords)

# Path to your local stopwords file
local_stopwords_path = 'english'

# Load the stopwords
stop_words = load_stopwords(local_stopwords_path)
app = Flask(__name__)
CORS(app)  # Enabling CORS

# Load the data from the JSON file
with open('data.json', 'r') as file:
    data = json.load(file)
    print("Data loaded successfully.")

def tokenize(text):
    """Tokenize the text into individual keywords or tokens, excluding stop words."""
    tokens = set(text.lower().split())
    return tokens.difference(stop_words)

def calculate_match_percentage(query_tokens, text_tokens):
    """Calculate the matching percentage based on the number of tokens that match."""
    if query_tokens:
        matching_tokens = query_tokens.intersection(text_tokens)
        return len(matching_tokens) / len(query_tokens)
    return 0

def fact_check(query, data, limit=None):
    print(f"Fact-checking the query: {query}")
    query_tokens = tokenize(query)
    scores = []

    for obj in data:
        headline_tokens = tokenize(obj["Headline"])
        claim_tokens = tokenize(obj["What_(Claim)"])
        img_tokens = tokenize(obj["img"]) if obj["img"] != "NA" else set()
        about_person_tokens = tokenize(obj["About_Person"]) if obj["About_Person"] != "NA" else set()
        about_subject_tokens = tokenize(obj["About_Subject"]) if obj["About_Subject"] != "NA" else set()
        
        headline_match = calculate_match_percentage(query_tokens, headline_tokens)
        claim_match = calculate_match_percentage(query_tokens, claim_tokens)
        img_match = calculate_match_percentage(query_tokens, img_tokens)
        about_person_match = calculate_match_percentage(query_tokens, about_person_tokens)
        about_subject_match = calculate_match_percentage(query_tokens, about_subject_tokens)
        
        avg_match = (headline_match + claim_match + img_match + about_person_match + about_subject_match) / 5
        scores.append((avg_match, obj))
    
    # Rank the results
    top_matches = sorted(scores, key=lambda x: x[0], reverse=True)
    if limit:
        top_matches = top_matches[:limit]
    print(f"Found {len(top_matches)} top matches.")
    return top_matches

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query', '')
    limit = request.json.get('limit', 10)
    results = fact_check(query, data, limit)
    response_data = [{"percentage": round(match[0]*100, 2), "data": match[1]} for match in results]
    print(f"Search completed for query: {query}")
    return jsonify(response_data)

@app.route('/searchAll', methods=['POST'])
def search_all():
    query = request.json.get('query', '')
    results = fact_check(query, data)
    response_data = [{"percentage": round(match[0]*100, 2), "data": match[1]} for match in results]
    print(f"SearchAll completed for query: {query}")
    return jsonify(response_data)

if __name__ == "__main__":
    print("Starting the server...")
    app.run(debug=True, port=3001)
