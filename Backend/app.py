from flask import Flask, request, jsonify
from flask_cors import CORS
import json

from werkzeug.utils import secure_filename
from DeepImageSearch import Load_Data, Search_Setup
import os
from sentence_transformers import SentenceTransformer, util

import torch  # Import torch for tensor operations
import pandas as pd
import numpy as np
import logging
from logging.handlers import RotatingFileHandler
from transformers import AutoModel, AutoTokenizer
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

# Log to console in DEBUG mode
if app.debug:
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    app.logger.addHandler(console)

app.logger.info("Flask application started")

# Load the data from the JSON file
with open("csvProcessing/hindi.json", "r") as file:
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
with open("csvProcessing/hindi.json", "r") as file:
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
    top_matches = sorted(scores, key=lambda x: x[0], reverse=True)[:limit]
    print(f"Found {len(top_matches)} top matches.")
    return top_matches


@app.route("/search", methods=["POST"])
def search():
    query = request.json.get("query", "")
    limit = request.json.get("limit", 10)
    # Adjust the fact_check call to correctly iterate through the updated data structure
    results = fact_check(query, data, limit)
    response_data = [
        {"percentage": round(match[0] * 100, 2), "data": match[1]} for match in results
    ]
    print(f"Search completed for query: {query}")
    return jsonify(response_data)


image_list = Load_Data().from_folder(["./ImageMatching/data"])
# Set up the search engine
st = Search_Setup(
    image_list=image_list, model_name="vgg19", pretrained=True, image_count=102
)
# Index the images
st.run_index()


# @app.route("/upload", methods=["POST"])
# def upload_file():
#     if "file" not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     file = request.files["file"]
#     if file.filename == "":
#         return jsonify({"error": "No selected file"}), 400


#     if file:
#         filename = secure_filename("test.jpg")
#         filepath = os.path.join("./", filename)
#         file.save(filepath)
#         try:
#             # Get similar images using the uploaded image
#             similar_images = st.get_similar_images(
#                 image_path=filepath, number_of_images=10
#             )
#             print(f"Found similar images: {similar_images}")
#             # Send back the similar images' paths or identifiers
#             return jsonify({"similar_images": similar_images})
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500

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
        try:
            similar_images = st.get_similar_images(image_path=filepath, number_of_images=10)
            
            response_data = []
            for img_info in similar_images:
                image_id = img_info["path"].split("_")[-1].split(".")[0]  # Assuming this gets the ID
                # Fetch the corresponding object from the JSON data using ID
                corresponding_object = data.get(image_id)
                if corresponding_object:
                    response_data.append({
                        "percentage": round(img_info["match_percentage"], 2),
                        "data": corresponding_object,
                    })
                else:
                    print(f"No corresponding object found for ID {image_id}")

            return jsonify(response_data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

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
with open("csvProcessing/hindi.json", "r", encoding="utf-8") as file:
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
                image_path=temp_image_path, number_of_images=10
            )

            response_data = []
            for img_info in similar_images:  # Iterate through the list of dictionaries
                # Extract the index from the image path
                image_index = (
                    int(img_info["path"].split("_")[-1].split(".")[0]) - 1
                )  # Adjust index to 0-based
                print(image_index)

                # Fetch the corresponding object from the JSON data
                corresponding_object = data[image_index]
                print(corresponding_object)

                # Append the object and its match percentage to the response data
                response_data.append(
                    {
                        "percentage": round(img_info["match_percentage"], 2),
                        "data": corresponding_object,
                    }
                )
                print("response_data", response_data)

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
    top_10_indices = np.argsort(cosine_similarities)[::-1][:10]

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
    file_path = "csvProcessing/hindi.json"

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


if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. You
    # can configure startup instructions by adding `entrypoint` to app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)
# [END gae_python3_app]
# [END gae_python38_app]
