from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
import json
# import google.generativeai as genai
from werkzeug.utils import secure_filename
from DeepImageSearch import Load_Data, Search_Setup
import os
# from sentence_transformers import SentenceTransformer, util
# import urllib.request

import torch  # Import torch for tensor operations
import pandas as pd
import numpy as np
import logging
from logging.handlers import RotatingFileHandler
# from transformers import AutoModel, AutoTokenizer, AutoModelForCausalLM
from scipy.spatial.distance import cosine
import requests  # Import requests to fetch image from URL
from PIL import Image, UnidentifiedImageError  # Import PIL to handle image operations
from io import BytesIO  # Import BytesIO to convert response content to image
import os
import shutil  # Import shutil for file operations
from flask_bcrypt import Bcrypt
from flask_session import Session
from config import ApplicationConfig
from models import db, User

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configure Logging
formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
handler = RotatingFileHandler("flask_app.log", maxBytes=10000, backupCount=3)
handler.setLevel(logging.WARNING)  # Adjust this level as needed
handler.setFormatter(formatter)
app.logger.addHandler(handler)
import csv
from datetime import datetime

import base64

app.config.from_object(ApplicationConfig)

bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
server_session = Session(app)
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    # Render the React app built files
    return render_template("index.html")


@app.route("/api/@me")
def get_current_user():
    user_id = session.get("user_id")
    print(user_id)
    print(session)

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.filter_by(id=user_id).first()
    return jsonify({"id": user.id, "email": user.email})


@app.route("/api/register", methods=["POST"])
def register_user():
    email = request.json["email"]
    password = request.json["password"]

    user_exists = User.query.filter_by(email=email).first() is not None

    if user_exists:
        return jsonify({"error": "User already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password)
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id

    return jsonify({"id": new_user.id, "email": new_user.email})


@app.route("/api/login", methods=["POST"])
def login_user():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401

    session["user_id"] = user.id

    return jsonify({"id": user.id, "email": user.email})


@app.route("/api/logout", methods=["POST"])
def logout_user():
    print("Attempting to logout:", session)

    # Check if 'user_id' is in the session
    if "user_id" not in session:
        print("No user_id found in session, cannot logout")
        return (
            jsonify({"error": "Unauthorized"}),
            401,
        )  # Return a 401 Unauthorized response

    # If 'user_id' is found, remove it from the session
    session.pop("user_id")
    print("Logout successful")
    return jsonify({"message": "Logout successful"}), 200


def log_query(query_type, query_content):
    # Convert image to base64 if it's a file
    if query_type == "image":
        image_binary = query_content.read()
        query_content = base64.b64encode(image_binary).decode("utf-8")
    with open("query_log.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write the time stamp, type of query, and the query/image/file sent
        writer.writerow([datetime.now(), query_type, query_content])


# ---------------------------------------------
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


# def tokenize(text):
#     """Tokenize the text into individual keywords or tokens, excluding stop words."""
#     tokens = set(text.lower().split())
#     return tokens.difference(stop_words)


# def calculate_match_percentage(query_tokens, text_tokens):
#     """Calculate the matching percentage based on the number of tokens that match."""
#     if query_tokens:
#         matching_tokens = query_tokens.intersection(text_tokens)
#         return len(matching_tokens) / len(query_tokens)
#     return 0


# def fact_check(query, data, limit=None):
#     print(f"Fact-checking the query: {query}")
#     query_tokens = tokenize(query)
#     scores = []

#     # Iterate through data.items() for the new dictionary structure
#     for id, obj in data.items():
#         headline_tokens = tokenize(obj["Headline"])
#         claim_tokens = tokenize(obj["What_(Claim)"])
#         # Adjust image and subject/person tokenization based on the presence of data
#         img_tokens = (
#             tokenize(obj["img"]) if "img" in obj and obj["img"] != "NA" else set()
#         )
#         about_person_tokens = (
#             tokenize(obj["About_Person"])
#             if "About_Person" in obj and obj["About_Person"] != "NA"
#             else set()
#         )
#         about_subject_tokens = (
#             tokenize(obj["About_Subject"])
#             if "About_Subject" in obj and obj["About_Subject"] != "NA"
#             else set()
#         )

#         # Calculate matches
#         headline_match = calculate_match_percentage(query_tokens, headline_tokens)
#         claim_match = calculate_match_percentage(query_tokens, claim_tokens)
#         img_match = calculate_match_percentage(query_tokens, img_tokens)
#         about_person_match = calculate_match_percentage(
#             query_tokens, about_person_tokens
#         )
#         about_subject_match = calculate_match_percentage(
#             query_tokens, about_subject_tokens
#         )

#         avg_match = (
#             headline_match
#             + claim_match
#             + img_match
#             + about_person_match
#             + about_subject_match
#         ) / 5
#         scores.append((avg_match, obj))

#     # Rank and limit the results
#     sorted_results = sorted(scores, key=lambda x: x[0], reverse=True)

#     # Filter out the results where the match is 1% or less
#     top_matches = [match for match in sorted_results if match[0] > 0.01]

#     print(f"Found {len(top_matches)} top matches with more than 1% match.")
#     return top_matches


# @app.route("/api/search", methods=["POST"])
# def search():
#     query = request.json.get("query", "")
#     # Log the query
#     log_query("text", query)
#     results = fact_check(query, data)
#     if len(results) == 0:
#         return (
#             jsonify(
#                 {
#                     "error": "Your search yielded 0 matches in our database, Please check your query"
#                 }
#             ),
#             404,
#         )

#     # print(results)

#     seen_headlines = set()  # Set to keep track of seen headlines
#     response_data_TFIDF = []
#     for match in results:
#         if match[0] > 0.01:  # Filter out the results where the match is 1% or less
#             headline = match[1]["Headline"]
#             # Check if headline has already been added
#             if headline not in seen_headlines:
#                 seen_headlines.add(headline)  # Mark headline as seen
#                 response_data_TFIDF.append(
#                     {"percentage": round(match[0] * 100, 2), "data": match[1]}
#                 )
#             # else:
#             # print(f"Duplicate headline found and skipped: {headline}")

#     # Format the top matches
#     seen_headlines_top = (
#         set()
#     )  # Initialize an empty set to keep track of seen headlines
#     top_matches = {}

#     for i, (_, match_data) in enumerate(results[:40], start=1):
#         headline = match_data["Headline"]
#         if (
#             headline not in seen_headlines_top
#         ):  # Check if the headline has not been seen before
#             seen_headlines_top.add(
#                 headline
#             )  # Add the headline to the set of seen headlines
#             top_matches[str(i)] = match_data  # Add the match data to top_matches
#     print(top_matches)
#     seen_headlines = set()  # Initialize a set to track seen headlines

#     gemini_input_objects = {}
#     for i, (_, match_data) in enumerate(results[:40], start=1):
#         headline = match_data["Headline"]
#         if headline not in seen_headlines:
#             seen_headlines.add(
#                 headline
#             )  # Add the headline to the set of seen headlines
#             gemini_input_objects[str(i)] = {
#                 "Story_Date": match_data["Story_Date"],
#                 "Headline": match_data["Headline"],
#                 "What_(Claim)": match_data["What_(Claim)"],
#                 "About_Subject": match_data["About_Subject"],
#                 "About_Person": match_data["About_Person"],
#                 "Story_URL": match_data["Story_URL"],
#             }

#         gemini_input_str = json.dumps(
#             gemini_input_objects, indent=2, ensure_ascii=False
#         )

#     prompt = f"""
# You are an advanced AI specializing in debunking fake news.

# You will be given a text (claim) and a set of news articles. Each news article will be in the form of a JSON object having the fields "Headline", "What_(Claim)", "About_Subject", and "About_Person" .  \n\n
# Your task is to compute the percentage similarity between the claim text and each news article.
# \n\n

# EXAMPLE_INPUT:\n
#       [ \n
#  "1": {{
#         "Story_URL": "https://www.vishvasnews.com/ai-check/fact-check-pm-modi/",\n
#         "Headline": "Fact Check: पीएम मोदी और अमेरिकी राष्ट्रपति जो बाइडेन की वायरल तस्वीरें AI निर्मित हैं",\n
#         "What_(Claim)": "पीएम मोदी और अमेरिकी राष्ट्रपति कुर्ता-पायजामा पहनकर टहल रहे हैं।",\n
#         "About_Subject": "PM ans USA President",\n
#         "About_Person": "Narendra Modi, Joe Biden ",
#         }},\n
# "2": {{\n
#         "Story_URL": "https://www.vishvas/act-check-artificially-generated-photo-of-elon-musk-in-moroccos-chefchaouen-goes-viral-as-real/",\n
#         "Headline": "Fact Check: मोरक्को की ‘ब्लू सिटी’ में नजर आ रहे एलन मस्क की यह तस्वीर असल नहीं, AI जनरेटेड है",\n
#         "What_(Claim)": "एलन मस्क मोरक्को में यात्रा कर रहे हैं",\n
#         "About_Subject": "AI generated image",\n
#         "About_Person": "Elon Musk"\n
#     }}\n\n
#     "3": {{
#         "Story_URL": "https://www.vishfact-check-uppsc-pcs-j-2018-result-candidate-list-viral-with-misleading-claim/",\n
#         "Headline": "Fact Check: UPPSC के पीसीएस-जे 2018 के सफल अभ्‍यर्थियों की अधूरी लिस्‍ट भ्रामक दावे से वायरल",\n
#         "What_(Claim)": "यह UPPSC के पीसीएस-जे का रिजल्ट है, जिसमें जनरल वर्ग के परीक्षार्थियों के नाम हैं।",\n
#         "About_Subject": "UPPCS PCS J Result",\n
#         "About_Person": "Akanksha Tiwari",\n
#     }}\n

# QUERY_CLAIM: “did elon musk go to morocco and the city”\n

#        Note: In this example "1", “2” & "3" are the indexes of the json objects in NEWS_OBJECTS.
# \n
# EXPECTED_OUTPUT_FORMAT:\n
# {{\n
# “1” : “0%”,\n
# “2” : “70%”,\n
# "3" : "6%"\n
# }}

#     \n\n
#     --------------end of example ----------------------------------------\n
# Here is the \n
# Query: "{query}"\n
# News Articles: {gemini_input_str}\n\n
# Here is the query again:\n
# Query: "{query}"\n\n
#     Please provide the similarity scores in the following JSON format, assigning higher percentages to articles that are more similar to the query:\n\n
# {{\n
#   "index": "match percentage",\n
# }}
 
#  """

#     # print(prompt)
#     # Gemini API call would go here, assuming `gemini_api_response` is the response from the API
#     # For demonstration, let's assume we receive a response like this:

#     api_keys = [
#         "AIzaSyDd26SvuTQqx5kIW50llUWnWCMtP4bZpWg",
#         "AIzaSyCXmFr_2SiyXrVBD8dAkp-usgCyXA-qH8E",
#         "AIzaSyCr7GxmtXmdS--QrjTAy4oQUjpn9qsPAPw",
#     ]
#     attempt = 0
#     max_attempts = 3
#     gemini_response = None
#     gemini_response_valid = False

#     while attempt < max_attempts and not gemini_response_valid:
#         try:
#             current_api_key = api_keys[attempt]
#             genai.configure(api_key=current_api_key)
#             model = genai.GenerativeModel("gemini-pro")
#             messages = [{"role": "user", "parts": [prompt]}]
#             safety_settings = [
#                 {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
#                 {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
#                 {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
#                 {
#                     "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#                     "threshold": "BLOCK_NONE",
#                 },
#                 {
#                     "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#                     "threshold": "BLOCK_NONE",
#                 },
#             ]
#             gemini_api_response = model.generate_content(
#                 messages,
#                 safety_settings=safety_settings,
#                 generation_config=genai.types.GenerationConfig(
#                     temperature=0.4,
#                 ),
#             )
#             response_text = gemini_api_response.text
#             print(response_text)
#             gemini_response_data = json.loads(
#                 response_text
#             )  # Attempt to parse the response

#             # try:
#             #     response_data = json.loads(response_text)
#             # except :
#             #     print("Parsing error" )
#             #     return jsonify(response_data_TFIDF)
#             if isinstance(gemini_response_data, dict):
#                 gemini_response_valid = True
#                 enhanced_response_data = []
#                 for index, percentage in gemini_response_data.items():
#                     if index in top_matches:
#                         # Append both the data from top_matches and the percentage from Gemini response
#                         # Ensure percentage is converted to an integer for sorting
#                         numeric_percentage = int(
#                             percentage.rstrip("%")
#                         )  # Remove '%' and convert to int

#                         if numeric_percentage > 60:

#                             enhanced_response_data.append(
#                                 {
#                                     "percentage": numeric_percentage,
#                                     "numeric_percentage": numeric_percentage,
#                                     "data": top_matches[index],
#                                 }
#                             )

#                 # Sort the enhanced_response_data by 'numeric_percentage' in descending order
#                 sorted_enhanced_response_data = sorted(
#                     enhanced_response_data,
#                     key=lambda x: x["numeric_percentage"],
#                     reverse=True,
#                 )

#                 # Remove the 'numeric_percentage' key from each item as it was only needed for sorting
#                 for item in sorted_enhanced_response_data:
#                     item.pop("numeric_percentage", None)
#                 print(sorted_enhanced_response_data)
#                 return jsonify(sorted_enhanced_response_data)

#             else:
#                 raise ValueError("Response format not as expected.")

#         except Exception as e:
#             print(f"Attempt {attempt + 1} failed: {str(e)}")
#             attempt += 1  # Move to the next attempt

#             # Assume response_text is a JSON string that looks like: {"1": "75%", "2": "50%", "3": "25%"}
#             # gemini_response = json.loads(response_text)
#             # print(gemini_response)
#             # print(top_matches)
#     if not gemini_response_valid:
#         return (
#             jsonify(
#                 {
#                     "error": "Failed to get a valid response from the API after multiple attempts."
#                 }
#             ),
#             500,
#         )

    # Prepare the final response data with enhanced match percentages


# ###################################################################################
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


@app.route("/api/upload", methods=["POST"])
def upload_file():
    file_path = "csvProcessing/allData.json"  # Ensure this path is correct
    data= {}
    # Load the current data from the JSON file or initialize as an empty dictionary if the file does not exist
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            filename = secure_filename("test.jpg")
            filepath = os.path.join("./", filename)
            file.save(filepath)
        except Exception as e:
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

        try:
            # Get similar images using the uploaded image
            similar_images = st.get_similar_images(
                image_path=filepath, number_of_images=20
            )
        except Exception as e:
            return (
                jsonify({"error": f"Error during image similarity search: {str(e)}"}),
                500,
            )

        try:
            data = {}
            with open("csvProcessing/allData.json", "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return jsonify({"error": "Data file not found"}), 500
        except json.JSONDecodeError:
            return jsonify({"error": "Error decoding JSON data"}), 500
        except Exception as e:
            return jsonify({"error": f"Error loading data: {str(e)}"}), 500

        try:
            response_data = []
            seen_urls = set()  # Set to keep track of URLs we've already added

            for img_info in similar_images:
                image_index = img_info["path"].split("_")[-1].split(".")[0]

                if image_index in data:
                    corresponding_object = data[image_index]
                    story_url = corresponding_object.get("Story_URL")

                    # Check if we've already added this story URL
                    if story_url not in seen_urls:
                        if img_info["match_percentage"] > 60:
                            response_data.append(
                                {
                                    "percentage": round(
                                        img_info["match_percentage"], 2
                                    ),
                                    "data": corresponding_object,
                                }
                            )
                            seen_urls.add(story_url)  # Mark this URL as seen

            return jsonify(response_data)
        except KeyError as e:
            return jsonify({"error": f"Data missing key: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"Error processing response data: {str(e)}"}), 500
    else:
        return jsonify({"error": "File processing failed"}), 500


# ###################################################################################

@app.route("/api/uploadImageURL", methods=["POST"])
def upload_image_url():
    file_path = "csvProcessing/allData.json"  # Ensure this path is correct
    data = {}
    # Load the current data from the JSON file or initialize as an empty dictionary if the file does not exist
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

    json_data = request.get_json()
    image_url = json_data.get("image_url")
    data = {}
    with open("csvProcessing/allData.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    if not image_url:
        return jsonify({"error": "No image URL provided"}), 400

    temp_image_path = "./temp_image.jpg"  # Define the path outside try-except block

    try:
        # Fetch the image from the URL
        response = requests.get(image_url, stream=True)

        # Check if the request was successful
        if response.status_code != 200:
            return (
                jsonify(
                    {
                        "error": f"Failed to fetch image from URL, status code: {response.status_code}"
                    }
                ),
                500,
            )

        try:
            # Create a PIL Image from the binary data
            image = Image.open(BytesIO(response.content))

            # Save the image to a temporary file
            image.save(temp_image_path)

        except UnidentifiedImageError:
            return (
                jsonify(
                    {
                        "error": "Cannot identify image file. Ensure the URL points directly to an image."
                    }
                ),
                400,
            )

        except Exception as e:
            return jsonify({"error": f"Error processing image: {str(e)}"}), 500

        # Proceed with your existing logic for handling uploaded images
        similar_images = st.get_similar_images(
            image_path=temp_image_path, number_of_images=20
        )

        data = {}
        with open("csvProcessing/allData.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        response_data = []
        seen_urls = set()  # Set to keep track of URLs we've already added

        for img_info in similar_images:
            image_index = img_info["path"].split("_")[-1].split(".")[0]

            if image_index in data:
                corresponding_object = data[image_index]
                story_url = corresponding_object.get("Story_URL")

                # Check if we've already added this story URL
                if story_url not in seen_urls:
                    if img_info["match_percentage"] > 60:
                        response_data.append(
                            {
                                "percentage": round(img_info["match_percentage"], 2),
                                "data": corresponding_object,
                            }
                        )
                        seen_urls.add(story_url)  # Mark this URL as seen
        return jsonify(response_data)

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching image: {str(e)}"}), 500

    except Exception as e:
        # Clean up the temporary file in case of an error
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        return jsonify({"error": str(e)}), 500


from BERTClasses import bm25, ftsent, bertscore, load_data, ensemble

# Load the documents at app start to avoid reloading them on each request
docs, origdata = load_data("csvProcessing/allData.json")

model = ensemble(docs, use_translation=True, orig_docs=origdata, use_date_level=1)
# model = ensemble(docs, use_translation=False, orig_docs=origdata)


def add_docs(filename):
    newdocs, neworig = load_data(filename)
    docs.extend(newdocs)
    origdata.extend(neworig)
    model.add_docs(newdocs, neworig)


@app.route("/api/appendDataIndividual", methods=["POST"])
def append_data_individual():
    request_data = request.get_json()
    result, status_code = append_story(request_data)
    print(result)
    return jsonify(result), status_code


@app.route("/api/appendDataCSV", methods=["POST"])
def append_data_csv():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join("/tmp", filename)
    file.save(filepath)

    expected_columns = {
        "Story Date",
        "Story URL",
        "Headline",
        "What (Claim)",
        "About Subject",
        "About Person",
        "Featured Image",
        "Tags",
    }
    successful_entries = 0
    duplicate_entries = 0
    failed_entries = 0
    error_details = []
    results = []

    with open(filepath, mode="r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        headers = set(csv_reader.fieldnames)
        missing_columns = expected_columns - headers
        if missing_columns:
            os.remove(filepath)
            return (
                jsonify(
                    {
                        "error": "The CSV file is missing the following required columns:",
                        "missing_columns": sorted(list(missing_columns)),
                    }
                ),
                400,
            )

        for row_number, row in enumerate(csv_reader, start=1):
            json_data = {
                "Story_Date": row.get("Story Date"),
                "Story_URL": row.get("Story URL"),
                "Headline": row.get("Headline"),
                "What_(Claim)": row.get("What (Claim)"),
                "About_Subject": row.get("About Subject"),
                "About_Person": row.get("About Person"),
                "img": row.get("Featured Image"),
                "tags": row.get("Tags"),
            }
            result, status_code = append_story(json_data)
            results.append(result)
            if status_code == 200:
                successful_entries += 1
            elif status_code == 400:
                duplicate_entries += 1
            elif status_code == 500:
                failed_entries += 1
                error_details.append({"row": row_number, "error": result["message"]})

    os.remove(filepath)

    return jsonify(
        {
            "message": f"Added {successful_entries} successful entries and discarded {duplicate_entries} duplicates. Failed to append {failed_entries} entries.",
            "results": results,
            "error_details": error_details,
        }
    ), (200 if failed_entries == 0 else 400)


def append_story(request_data):
    file_path = "csvProcessing/allData.json"  # Ensure this path is correct

    # Load the current data from the JSON file or initialize as an empty dictionary if the file does not exist
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            file_data = json.load(file)
    else:
        file_data = {}

    # print(file_data)

    # Check for duplicate entries based on Story_URL
    if any(
        story["Story_URL"] == request_data["Story_URL"] for story in file_data.values()
    ):
        return {"message": "Story URL already exists. No data appended."}, 400

    # Generate a new index for the new story
    new_index = str(max(map(int, file_data.keys()), default=0) + 1)
    file_data[new_index] = request_data

    # Save new data temporarily for model processing
    temp_file_path = f"csvProcessing/temp_new_data_{new_index}.json"
    with open(temp_file_path, "w", encoding="utf-8") as temp_file:
        json.dump({new_index: request_data}, temp_file, ensure_ascii=False, indent=4)

    # Add new documents to the model
    add_docs(temp_file_path)
    os.remove(temp_file_path)  # Clean up the temporary file

    # Handle image downloading and indexing
    if "img" in request_data and request_data["img"]:
        image_url = request_data["img"]
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            image_filename = f"image_{new_index}.jpg"
            image_path = os.path.join("./data", image_filename)
            with open(image_path, "wb") as f:
                f.write(image_response.content)

            # Add the image to the index
            try:
                st.add_images_to_index([image_path])
            except Exception as e:
                return {"message": f"Failed to index image: {str(e)}"}, 500
        else:
            return {"message": "Failed to download image."}, 500

    # Write the updated data back to the JSON file
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(file_data, file, ensure_ascii=False, indent=4)

    # Optionally restart the server if necessary
    # restart_server()

    return {"message": "Data appended and image indexed successfully"}, 200


@app.route("/api/ensemble", methods=["POST"])
def rank_documents_bm25_bert():
    req = request.json
    query = req.get("query", "")
    log_query("text", query)

    data = []
    with open("csvProcessing/allData.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    print("Data loaded successfully.")

    # Using combined BM25 and BERTScore model to rank documents
    idx, scores = model.rank(query)
    results = []
    print(type(idx))
    percent = (
        round(20 * max(list(scores[:3]) + [model.match_percent(query, origdata[idx[0]])] )) * 5
        if len(idx) > 0
        else None
    )

    origkeys = [origdata[i]['key'] for i in idx]

    for doc_id, score in zip(origkeys[:10], scores[:10]):
        # doc_id = str(i)  # Convert index to integer
        print(doc_id)
        # doc_obj = data[doc_id]  # Access the corresponding document object

        results.append(
            {
                "percentage": percent,
                "data": data[doc_id],  # Include the whole news object
            }
        )
    return jsonify(results)


def rank_documents_bm25_bert_trends():
    req = request.json
    query = req.get("query", "")
    data = []
    with open("csvProcessing/allData.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    print("Data loaded successfully trends")

    # Using combined BM25 and BERTScore model to rank documents
    # model.use_date_level = 1

    idx, scores = model.rank(query)
    # model.use_date_level = 1
    results = []
    print(type(idx))
    percent = (
        round(20 * max(scores[:3])) * 5
        if len(idx) > 0
        else None
    )

    origkeys = [origdata[i]["key"] for i in idx]

    for doc_id, score in zip(origkeys[:10], scores[:10]):
        # doc_id = str(i)  # Convert index to integer
        print(doc_id)
        # doc_obj = data[doc_id]  # Access the corresponding document object

        results.append(
            {
                "percentage": percent,
                "data": data[doc_id],  # Include the whole news object
            }
        )
    return jsonify(results)


from google_trends import daily_trends, realtime_trends

import threading


def start_scheduler():
    from scheduler import run_scheduler

    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    print("Starting scheduler thread...")
    scheduler_thread.start()
start_scheduler()


@app.route("/api/top-trends", methods=["GET"])
def top_trends():
    try:
        # Load the cached results from the file
        with open("top_trends_cache.json", "r", encoding="utf-8") as cache_file:
            cached_data = json.load(cache_file)
        return jsonify(cached_data)
    except Exception as e:
        print(f"Error fetching cached trends: {str(e)}")
        return jsonify({"error": str(e)}), 500


import re
from datetime import datetime, timedelta
# Load the data from the JSON file
# Load the data from the JSON file
with open("csvProcessing/allData.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    print("Data loaded successfully.")


def remove_ordinal_suffix(date_str):
    # Remove ordinal suffixes: 1st, 2nd, 3rd, 4th, etc.
    return re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)


def parse_story_date(story_date):
    story_date = remove_ordinal_suffix(story_date)
    try:
        return datetime.strptime(story_date, "%d %b %Y")
    except ValueError:
        return None


def replace_year_safe(date, year):
    try:
        return date.replace(year=year)
    except ValueError:
        # Handle invalid dates, like 29th Feb on non-leap years
        return None


@app.route("/api/stories-by-date", methods=["POST"])
def stories_by_date():
    client_data = request.json
    specified_date_str = client_data.get("date", "")
    if not specified_date_str:
        return jsonify({"error": "No date provided"}), 400

    try:
        specified_date = datetime.strptime(specified_date_str, "%d %b %Y")
        print(specified_date)
    except ValueError:
        print(f"Invalid date format {specified_date_str}")
        return jsonify({"error": f"Invalid date format {specified_date_str}"}), 400

    start_date = specified_date - timedelta(days=1)
    end_date = specified_date + timedelta(days=1)

    matching_stories = []

    for story_id, story in data.items():
        story_date_str = story.get("Story_Date", "")
        story_date = parse_story_date(story_date_str)

        if story_date:
            story_date_this_year = replace_year_safe(story_date, specified_date.year)
            if story_date_this_year and start_date <= story_date_this_year <= end_date:
                matching_stories.append(
                    {
                        "percentage": 100,
                        "data": story,
                        "original_date": story_date,
                    }  # Store original date for sorting
                )

    # Sort the matching stories by 'original_date' in descending order
    matching_stories.sort(key=lambda x: x["original_date"], reverse=True)

    # Remove the 'original_date' key before sending the response
    for story in matching_stories:
        del story["original_date"]

    return jsonify(matching_stories)

if __name__ == "__main__":
    # start_scheduler()


    app.run(host="127.0.0.1", port=8080, debug=True, use_reloader=False)
# [END gae_python3_app]
# [END gae_python38_app]
