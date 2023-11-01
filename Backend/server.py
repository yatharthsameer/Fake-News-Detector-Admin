from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # This will allow all origins. Be sure to restrict this in production.

# Load the data from the JSON file
with open('data.json', 'r') as file:
    data = json.load(file)

def tokenize(text):
    """Tokenize the text into individual keywords or tokens."""
    return set(text.lower().split())

def calculate_match_percentage(query_tokens, text_tokens):
    """Calculate the matching percentage based on the number of tokens that match."""
    matching_tokens = query_tokens.intersection(text_tokens)
    return len(matching_tokens) / len(query_tokens)

def fact_check(query, data, limit=None):
    query_tokens = tokenize(query)
    scores = []

    # Match against Headlines, Claims, and additional fields
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
        
        # Average of all match percentages
        avg_match = (headline_match + claim_match + img_match + about_person_match + about_subject_match) / 5
        
        scores.append((avg_match, obj))

    # Rank and extract top matches
    top_matches = sorted(scores, key=lambda x: x[0], reverse=True)
    if limit:
        top_matches = top_matches[:limit]
    
    return top_matches


@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query', '')
    results = fact_check(query, data,10)
    # Convert results into a more structured format for the client
    response_data = [{"percentage": round(match[0]*100, 2), "data": match[1]} for match in results]
    return jsonify(response_data)
@app.route('/searchAll', methods=['POST'])
def search_all():
    query = request.json.get('query', '')
    results = fact_check(query, data)
    
    # Return all results
    response_data = [{"percentage": round(match[0]*100, 2), "data": match[1]} for match in results]
    
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True, port=3001)
