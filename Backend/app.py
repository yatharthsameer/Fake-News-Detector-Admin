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
with open("data_with_images_part2.json", "r") as file:
    data = json.load(file)
    print("Data loaded successfully.")


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
            # Get similar images using the uploaded image
            similar_images = st.get_similar_images(
                image_path=filepath, number_of_images=10
            )
            print(f"Found similar images: {similar_images}")

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
                print("response_data",response_data)

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
with open("data_with_images_part2.json", "r") as file:
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
    query_embedding = get_embedding(query)  # This should be 1-D

    # Compute cosine similarities, ensuring embeddings are 1-D
    cosine_similarities = [
        1 - cosine(query_embedding, emb.squeeze()) for emb in embeddings
    ]  # Use .squeeze() to make 1-D

    # Get the top 10 most similar indices and their scores
    top_10_indices = np.argsort(cosine_similarities)[::-1][:10]
    top_10_scores = np.array(cosine_similarities)[top_10_indices]

    # Prepare the response data
    response_data = []
    for index, score in zip(top_10_indices, top_10_scores):
        matched_item = {
            "percentage": round(score * 100, 2),
            "data": data[index],  # Use the item from `data.json` directly
        }
        response_data.append(matched_item)

    return jsonify(response_data)


@app.route("/appendData", methods=["POST"])
def append_story():
    # Extract data from the request
    request_data = request.get_json()
    print(request_data)

    # Define the path for the JSON file where data will be appended
    file_path = "data_with_images_part2.json"

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
