from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import google.generativeai as genai
from werkzeug.utils import secure_filename
from DeepImageSearch import Load_Data, Search_Setup
import os
from sentence_transformers import SentenceTransformer, util

import torch  # Import torch for tensor operations
import pandas as pd
import numpy as np
import logging
from logging.handlers import RotatingFileHandler
from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM
from scipy.spatial.distance import cosine
import requests  # Import requests to fetch image from URL
from PIL import Image, UnidentifiedImageError  # Import PIL to handle image operations
from io import BytesIO  # Import BytesIO to convert response content to image
import os
import shutil  # Import shutil for file operations


app = Flask(__name__)
CORS(app)  # Enabling CORS
# Configure Logging
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
handler = RotatingFileHandler("flask_app.log", maxBytes=10000, backupCount=3)
handler.setLevel(logging.WARNING)  # Adjust this level as needed
handler.setFormatter(formatter)
app.logger.addHandler(handler)
import csv
from datetime import datetime

import base64


def log_query(query_type, query_content):
    # Convert image to base64 if it's a file
    if query_type == "image":
        image_binary = query_content.read()
        query_content = base64.b64encode(image_binary).decode("utf-8")
    with open("query_log.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write the time stamp, type of query, and the query/image/file sent
        writer.writerow([datetime.now(), query_type, query_content])


# Log to console in DEBUG mode
if app.debug:
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    app.logger.addHandler(console)

app.logger.info("Flask application started")

# Load the data from the JSON file
with open("csvProcessing/allData.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    print("Data loaded successfully.")
import nltk
from nltk.corpus import stopwords
from werkzeug.utils import secure_filename
from DeepImageSearch import Load_Data, Search_Setup
import os


# Define a function to load stopwords from a local file
def load_stopwords(path):
    with open(path, "r") as file:
        stopwords = file.read().splitlines()
    return set(stopwords)


# Path to your local stopwords file
local_stopwords_path = "english"

# Load the stopwords
stop_words = load_stopwords(local_stopwords_path)


# Load the data from the JSON file
with open("csvProcessing/allData.json", "r") as file:
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

    # Iterate through data.items() for the new dictionary structure
    for id, obj in data.items():
        headline_tokens = tokenize(obj["Headline"])
        claim_tokens = tokenize(obj["What_(Claim)"])
        # Adjust image and subject/person tokenization based on the presence of data
        img_tokens = (
            tokenize(obj["img"]) if "img" in obj and obj["img"] != "NA" else set()
        )
        about_person_tokens = (
            tokenize(obj["About_Person"])
            if "About_Person" in obj and obj["About_Person"] != "NA"
            else set()
        )
        about_subject_tokens = (
            tokenize(obj["About_Subject"])
            if "About_Subject" in obj and obj["About_Subject"] != "NA"
            else set()
        )

        # Calculate matches
        headline_match = calculate_match_percentage(query_tokens, headline_tokens)
        claim_match = calculate_match_percentage(query_tokens, claim_tokens)
        img_match = calculate_match_percentage(query_tokens, img_tokens)
        about_person_match = calculate_match_percentage(
            query_tokens, about_person_tokens
        )
        about_subject_match = calculate_match_percentage(
            query_tokens, about_subject_tokens
        )

        avg_match = (
            headline_match
            + claim_match
            + img_match
            + about_person_match
            + about_subject_match
        ) / 5
        scores.append((avg_match, obj))

    # Rank and limit the results
    sorted_results = sorted(scores, key=lambda x: x[0], reverse=True)

    # Filter out the results where the match is 1% or less
    top_matches = [match for match in sorted_results if match[0] > 0.01]

    print(f"Found {len(top_matches)} top matches with more than 1% match.")
    return top_matches


@app.route("/search", methods=["POST"])
def search():
    query = request.json.get("query", "")
    # Log the query
    log_query("text", query)
    results = fact_check(query, data)
    if len(results) == 0:
        return jsonify({"error": "Your search yielded 0 matches in our database, Please check your query"}), 404

    # print(results)

    seen_headlines = set()  # Set to keep track of seen headlines
    response_data_TFIDF = []
    for match in results:
        if match[0] > 0.01:  # Filter out the results where the match is 1% or less
            headline = match[1]["Headline"]
            # Check if headline has already been added
            if headline not in seen_headlines:
                seen_headlines.add(headline)  # Mark headline as seen
                response_data_TFIDF.append(
                    {"percentage": round(match[0] * 100, 2), "data": match[1]}
                )
            # else:
            # print(f"Duplicate headline found and skipped: {headline}")

    # Format the top matches
    seen_headlines_top = set()  # Initialize an empty set to keep track of seen headlines
    top_matches = {}

    for i, (_, match_data) in enumerate(results[:40], start=1):
        headline = match_data["Headline"]
        if (
            headline not in seen_headlines_top
        ):  # Check if the headline has not been seen before
            seen_headlines_top.add(
                headline
            )  # Add the headline to the set of seen headlines
            top_matches[str(i)] = match_data  # Add the match data to top_matches
    print(top_matches)
    seen_headlines = set()  # Initialize a set to track seen headlines

    gemini_input_objects = {}
    for i, (_, match_data) in enumerate(results[:40], start=1):
        headline = match_data["Headline"]
        if headline not in seen_headlines:
            seen_headlines.add(headline)  # Add the headline to the set of seen headlines
            gemini_input_objects[str(i)] = {
                "Story_Date": match_data["Story_Date"],
                "Headline": match_data["Headline"],
                "What_(Claim)": match_data["What_(Claim)"],
                "About_Subject": match_data["About_Subject"],
                "About_Person": match_data["About_Person"],
                "Story_URL": match_data["Story_URL"],
            }

        gemini_input_str = json.dumps(gemini_input_objects, indent=2, ensure_ascii=False)

    prompt = f"""
You are an advanced AI specializing in debunking fake news.

You will be given a text (claim) and a set of news articles. Each news article will be in the form of a JSON object having the fields "Headline", "What_(Claim)", "About_Subject", and "About_Person" .  \n\n
Your task is to compute the percentage similarity between the claim text and each news article.
\n\n

EXAMPLE_INPUT:\n
      [ \n
 "1": {{
        "Story_URL": "https://www.vishvasnews.com/ai-check/fact-check-pm-modi/",\n
        "Headline": "Fact Check: पीएम मोदी और अमेरिकी राष्ट्रपति जो बाइडेन की वायरल तस्वीरें AI निर्मित हैं",\n
        "What_(Claim)": "पीएम मोदी और अमेरिकी राष्ट्रपति कुर्ता-पायजामा पहनकर टहल रहे हैं।",\n
        "About_Subject": "PM ans USA President",\n
        "About_Person": "Narendra Modi, Joe Biden ",
        }},\n
"2": {{\n
        "Story_URL": "https://www.vishvas/act-check-artificially-generated-photo-of-elon-musk-in-moroccos-chefchaouen-goes-viral-as-real/",\n
        "Headline": "Fact Check: मोरक्को की ‘ब्लू सिटी’ में नजर आ रहे एलन मस्क की यह तस्वीर असल नहीं, AI जनरेटेड है",\n
        "What_(Claim)": "एलन मस्क मोरक्को में यात्रा कर रहे हैं",\n
        "About_Subject": "AI generated image",\n
        "About_Person": "Elon Musk"\n
    }}\n\n
    "3": {{
        "Story_URL": "https://www.vishfact-check-uppsc-pcs-j-2018-result-candidate-list-viral-with-misleading-claim/",\n
        "Headline": "Fact Check: UPPSC के पीसीएस-जे 2018 के सफल अभ्‍यर्थियों की अधूरी लिस्‍ट भ्रामक दावे से वायरल",\n
        "What_(Claim)": "यह UPPSC के पीसीएस-जे का रिजल्ट है, जिसमें जनरल वर्ग के परीक्षार्थियों के नाम हैं।",\n
        "About_Subject": "UPPCS PCS J Result",\n
        "About_Person": "Akanksha Tiwari",\n
    }}\n

QUERY_CLAIM: “did elon musk go to morocco and the city”\n

       Note: In this example "1", “2” & "3" are the indexes of the json objects in NEWS_OBJECTS.
\n
EXPECTED_OUTPUT_FORMAT:\n
{{\n
“1” : “0%”,\n
“2” : “70%”,\n
"3" : "6%"\n
}}

    \n\n
    --------------end of example ----------------------------------------\n
Here is the \n
Query: "{query}"\n
News Articles: {gemini_input_str}\n\n
Here is the query again:\n
Query: "{query}"\n\n
    Please provide the similarity scores in the following JSON format, assigning higher percentages to articles that are more similar to the query:\n\n
{{\n
  "index": "match percentage",\n
}}
 
 """

    # print(prompt)
    # Gemini API call would go here, assuming `gemini_api_response` is the response from the API
    # For demonstration, let's assume we receive a response like this:

    api_keys = [
        "AIzaSyDd26SvuTQqx5kIW50llUWnWCMtP4bZpWg",
        "AIzaSyCXmFr_2SiyXrVBD8dAkp-usgCyXA-qH8E",
        "AIzaSyCr7GxmtXmdS--QrjTAy4oQUjpn9qsPAPw",
    ]
    attempt = 0
    max_attempts = 3
    gemini_response = None
    gemini_response_valid = False

    while attempt < max_attempts and not gemini_response_valid:
        try:
            current_api_key = api_keys[attempt]
            genai.configure(api_key=current_api_key)
            model = genai.GenerativeModel("gemini-pro")
            messages = [{"role": "user", "parts": [prompt]}]
            safety_settings = [
                {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]
            gemini_api_response = model.generate_content(
                messages,
                safety_settings=safety_settings,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                ),
            )
            response_text = gemini_api_response.text
            print(response_text)
            gemini_response_data = json.loads(response_text)  # Attempt to parse the response

            # try:
            #     response_data = json.loads(response_text)
            # except :
            #     print("Parsing error" )
            #     return jsonify(response_data_TFIDF)
            if isinstance(gemini_response_data, dict) :
                gemini_response_valid = True
                enhanced_response_data = []
                for index, percentage in gemini_response_data.items():
                    if index in top_matches:
                        # Append both the data from top_matches and the percentage from Gemini response
                        # Ensure percentage is converted to an integer for sorting
                        numeric_percentage = int(
                            percentage.rstrip("%")
                        )  # Remove '%' and convert to int

                        if numeric_percentage > 60:

                            enhanced_response_data.append(

                                {
                                    "percentage": numeric_percentage,
                                    "numeric_percentage": numeric_percentage,
                                    "data": top_matches[index],
                                }
                            )

                # Sort the enhanced_response_data by 'numeric_percentage' in descending order
                sorted_enhanced_response_data = sorted(
                    enhanced_response_data, key=lambda x: x["numeric_percentage"], reverse=True
                )

                # Remove the 'numeric_percentage' key from each item as it was only needed for sorting
                for item in sorted_enhanced_response_data:
                    item.pop("numeric_percentage", None)
                print(sorted_enhanced_response_data)
                return jsonify(sorted_enhanced_response_data)

            else:
                raise ValueError("Response format not as expected.")

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            attempt += 1  # Move to the next attempt

            # Assume response_text is a JSON string that looks like: {"1": "75%", "2": "50%", "3": "25%"}
            # gemini_response = json.loads(response_text)
            # print(gemini_response)
            # print(top_matches)
    if not gemini_response_valid:
        return (
            jsonify(
                {
                    "error": "Failed to get a valid response from the API after multiple attempts."
                }
            ),
            500,
        )

    # Prepare the final response data with enhanced match percentages


image_list = Load_Data().from_folder(["./ImageMatching/data"])
# Set up the search engine
st = Search_Setup(
    image_list=image_list,
    model_name="resnet50",
    pretrained=True,
    image_count=8707,
)
# Index the images
st.run_index()


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename("test.jpg")
        filepath = os.path.join("./", filename)
        file.save(filepath)

            # Get similar images using the uploaded image
        similar_images = st.get_similar_images(
            image_path=filepath, number_of_images=20
        )
        print(f"Found similar images: {similar_images}")


        response_data = []
        for img_info in similar_images:
            # Extract the numerical index from the image filename
            image_index = img_info["path"].split('_')[-1].split('.')[0]

            # Use the extracted index to access the corresponding object in data
            if image_index in data:
                corresponding_object = data[image_index]
                if img_info["match_percentage"] > 60:

                # Append the relevant details to response_data
                    response_data.append({
                        "percentage": round(img_info["match_percentage"], 2),
                        "data": corresponding_object
                    })

        return jsonify(response_data)
    else:
        return jsonify({"error": "File processing failed"}), 500


# Load the pre-computed embeddings and associated texts from the CSV file
# embeddings_df = pd.read_csv("text_embeddings.csv")
# # Extract embeddings and convert them to float32
# embeddings = embeddings_df.drop(columns=["Text"]).values.astype(np.float32)
# # Extract the original texts for reference
# texts = embeddings_df["Text"].tolist()

# # Initialize the Sentence Transformer model
# model = SentenceTransformer("all-MiniLM-L6-v2")


# @app.route("/searchEmbed", methods=["POST"])
# def search_embed():
#     # Get the query from the POST request
#     print("request.json", request.json)
#     query = request.json.get("query", "")
#     print("query", query)
#     # Encode the query to get its embedding
#     query_embedding = model.encode(query).astype(np.float32)

#     # Compute cosine similarity between the query embedding and pre-computed embeddings
#     cosine_similarities = util.pytorch_cos_sim(query_embedding, embeddings)[0].numpy()

#     # Get the top 10 most similar indices and their scores
#     top_10_indices = np.argsort(cosine_similarities)[::-1][:10]
#     top_10_scores = cosine_similarities[top_10_indices]

#     # Prepare the response data
#     response_data = []
#     for index, score in zip(top_10_indices, top_10_scores):
#         # Directly use the corresponding item from `data`
#         matched_item = data[index]
#         response_data.append(
#             {
#                 "percentage": round(score * 100, 2),
#                 "data": matched_item,  # Use the item from `data.json` directly
#             }
#         )
#         print("response_data", response_data)

#     # Return the top 10 most similar texts along with their similarity scores

#     print("response_data", jsonify(response_data))
#     return jsonify(response_data)

# Load IndicBERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-bert")
model = AutoModel.from_pretrained("ai4bharat/indic-bert")

# Load the data from the JSON file
with open("csvProcessing/allData.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    print("Data loaded successfully.")

# Load the pre-computed embeddings and associated texts from the CSV file
# Note: Ensure you have regenerated these embeddings using IndicBERT
embeddings_df = pd.read_csv("indicbert_text_embeddings.csv")
embeddings = embeddings_df.drop(columns=["Text"]).values.astype(np.float32)
texts = embeddings_df["Text"].tolist()


def get_embedding(text):
    """Generate embeddings for the given text using IndicBERT."""
    inputs = tokenizer(
        text, return_tensors="pt", padding=True, truncation=True, max_length=512
    )
    with torch.no_grad():
        outputs = model(**inputs)
        # Using mean pooling to get a fixed size embedding vector
        embedding = (
            outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        )  # Ensure the output is 1-D
    return embedding


@app.route("/uploadImageURL", methods=["POST"])
def upload_image_url():
    json_data = request.get_json()
    image_url = json_data.get("image_url")

    if not image_url:
        return jsonify({"error": "No image URL provided"}), 400

    temp_image_path = "./temp_image.jpg"  # Define the path outside try-except block

    try:
        # Fetch the image from the URL
        response = requests.get(image_url, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            # Create a PIL Image from the binary data
            image = Image.open(BytesIO(response.content))

            # Save the image to a temporary file
            image.save(temp_image_path)

            # Proceed with your existing logic for handling uploaded images
            similar_images = st.get_similar_images(
                image_path=temp_image_path, number_of_images=20
            )

            response_data = []
            for img_info in similar_images:  # Iterate through the list of dictionaries
                # Extract the index from the image path
                image_index = img_info["path"].split('_')[-1].split('.')[0]

                # Use the extracted index to access the corresponding object in data
                if image_index in data:
                    corresponding_object = data[image_index]
                    if img_info["match_percentage"] > 60:

                        # Append the relevant details to response_data
                        response_data.append(
                            {
                                "percentage": round(img_info["match_percentage"], 2),
                                "data": corresponding_object,
                            }
                        )

            return jsonify(response_data)

        else:
            return jsonify({"error": "Failed to fetch image from URL"}), 500
    except UnidentifiedImageError as e:
        return (
            jsonify(
                {
                    "error": "Cannot identify image file. Ensure the URL points directly to an image."
                }
            ),
            400,
        )
    except Exception as e:
        # Clean up the temporary file in case of an error
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        return jsonify({"error": str(e)}), 500


@app.route("/searchEmbed", methods=["POST"])
def search_embed():
    query = request.json.get("query", "")
    query_embedding = get_embedding(
        query
    )  # Assuming get_embedding is defined elsewhere

    # Load embeddings and IDs
    embeddings_df = pd.read_csv("indicbert_text_embeddings.csv")
    embeddings = embeddings_df.drop(columns=["ID", "Text"]).values
    ids = embeddings_df["ID"].values

    cosine_similarities = [1 - cosine(query_embedding, emb) for emb in embeddings]
    top_10_indices = np.argsort(cosine_similarities)[::-1][:15]

    response_data = []
    for index in top_10_indices:
        id = ids[index]
        matched_item = data.get(str(id))  # Ensure IDs are strings if necessary
        if matched_item:
            response_data.append(
                {
                    "percentage": round(cosine_similarities[index] * 100, 2),
                    "data": matched_item,
                }
            )

    return jsonify(response_data)


@app.route("/appendData", methods=["POST"])
def append_story():
    # Extract data from the request
    request_data = request.get_json()
    print(request_data)

    # Define the path for the JSON file where data will be appended
    file_path = "csvProcessing/allData.json"

    # Check if the file exists. If not, create an empty list to start with
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False)

    # Open the file to read the current data
    with open(file_path, "r+", encoding="utf-8") as file:
        # Read the current data in the file
        file_data = json.load(file)

        # Check if Story_URL is already present
        existing_story = next(
            (
                item
                for item in file_data
                if item["Story_URL"] == request_data["Story_URL"]
            ),
            None,
        )
        if existing_story is not None:
            # If present, do not append and return a message indicating so
            return (
                jsonify({"message": "Story URL already exists. No data appended."}),
                400,
            )

        # If Story_URL is not present, append the new data (request_data) to the file's data
        file_data.append(request_data)
        # Set file's current position at offset.
        file.seek(0)
        # Clear the file content
        file.truncate()
        # Convert back to json and write in the file
        json.dump(file_data, file, ensure_ascii=False, indent=4)

    # Send back a response to indicate success
    return jsonify({"message": "Data appended successfully"}), 200

from BERTClasses import bm25, ftsent, bertscore, load_data, ensemble

# Load the documents at app start to avoid reloading them on each request
docs,origdata = load_data("csvProcessing/allData.json")

model = ensemble(docs)

print("Models loaded successfully.")


@app.route("/ensemble", methods=["POST"])
def rank_documents_bm25_bert():
    req = request.json
    query = req.get("query", "")

    # Using combined BM25 and BERTScore model to rank documents
    idx, scores = model.rank(query, thresh=0.8)
    results = []
    print(type(idx))
    percent = (
        round(20 * max(scores[0], model.match_percent(query, origdata[idx[0]]))) * 5
        if len(idx) > 0
        else None
    )
    
    for i, score in zip(idx[:10], scores[:10]):
        doc_id = str(i + 1)  # Convert index to integer
        print(doc_id)
        doc_obj = data[doc_id]  # Access the corresponding document object

        results.append(
            {
                "percentage": percent,
                "data": data[doc_id],  # Include the whole news object
            }
        )
    return jsonify(results)


if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. You
    # can configure startup instructions by adding `entrypoint` to app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)
# [END gae_python3_app]
# [END gae_python38_app]
