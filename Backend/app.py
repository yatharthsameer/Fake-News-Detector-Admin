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


# ###################################################################################
# Function to count the number of image files in the folder
def count_images_in_folder(folder_path):
    image_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".gif",
    )  # Common image file extensions
    return sum(
        1
        for filename in os.listdir(folder_path)
        if filename.lower().endswith(image_extensions)
    )


# Load images from the folder
image_list = Load_Data().from_folder(["data"])

# Determine the number of images in the data folder
image_count = count_images_in_folder("data")
# Set up the search engine
st = Search_Setup(
    image_list=image_list,
    model_name="resnet50",
    pretrained=True,
    image_count=image_count,
)


# Index the images
st.run_index()

from PIL import Image


@app.route("/api/upload", methods=["POST"])
def upload_file():
    file_path = "csvProcessing/allData.json"  # Ensure this path is correct
    data = {}
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
            filename = "test.jpg"
            filepath = os.path.join("./", filename)

            # Check if the uploaded file is PNG and convert it to JPG
            image = Image.open(file.stream)
            if image.format == "PNG":
                image = image.convert("RGB")  # Convert to RGB
                image.save(filepath, "JPEG")
            else:
                image.save(filepath)  # Save as JPG directly if not PNG

        except Exception as e:
            return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

        try:
            # Get similar images using the uploaded image
            similar_images = st.get_similar_images(
                image_path=filepath, number_of_images=30
            )
        except Exception as e:
            return (
                jsonify({"error": f"Error during image similarity search: {str(e)}"}),
                500,
            )

        try:
            response_data = {}
            seen_urls = set()  # Set to keep track of URLs we've already added

            for img_info in similar_images:
                # Extract the story index from the image filename
                image_filename = os.path.basename(img_info["path"])
                print("image_filename", image_filename)
                image_parts = image_filename.split("_")
                story_index = image_parts[1]  # This is the index of the story object

                if story_index in data:
                    corresponding_object = data[story_index]
                    story_url = corresponding_object.get("Story_URL")

                    if story_url not in seen_urls:
                        # If the story is already in response_data, check if the new match_percentage is higher
                        if story_index in response_data:
                            if (
                                img_info["match_percentage"]
                                > response_data[story_index]["percentage"]
                            ):
                                response_data[story_index]["percentage"] = round(
                                    img_info["match_percentage"], 2
                                )
                        else:
                            response_data[story_index] = {
                                "percentage": round(img_info["match_percentage"], 2),
                                "data": corresponding_object,
                            }
                        seen_urls.add(story_url)  # Mark this URL as seen

            # Convert response_data to a list, sorted by the highest match percentage
            sorted_response = [
                {"percentage": val["percentage"], "data": val["data"]}
                for val in sorted(
                    response_data.values(), key=lambda x: x["percentage"], reverse=True
                )
            ]

            return jsonify(sorted_response)
        except KeyError as e:
            return jsonify({"error": f"Data missing key: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"Error processing response data: {str(e)}"}), 500
    else:
        return jsonify({"error": "File processing failed"}), 500


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

            # Check if the image is PNG and convert to JPG
            if image.format == "PNG":
                image = image.convert("RGB")
                image.save(temp_image_path, "JPEG")
            else:
                image.save(temp_image_path)  # Save as JPG directly if not PNG

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

        # Proceed with logic for handling uploaded images
        similar_images = st.get_similar_images(
            image_path=temp_image_path, number_of_images=20
        )

        try:
            response_data = {}
            seen_urls = set()  # Set to keep track of URLs we've already added

            for img_info in similar_images:
                # Extract the story index from the image filename
                image_filename = os.path.basename(img_info["path"])
                image_parts = image_filename.split("_")
                story_index = image_parts[1]  # This is the index of the story object

                if story_index in data:
                    corresponding_object = data[story_index]
                    story_url = corresponding_object.get("Story_URL")

                    if story_url not in seen_urls:
                        # If the story is already in response_data, check if the new match_percentage is higher
                        if story_index in response_data:
                            if (
                                img_info["match_percentage"]
                                > response_data[story_index]["percentage"]
                            ):
                                response_data[story_index]["percentage"] = round(
                                    img_info["match_percentage"], 2
                                )
                        else:
                            response_data[story_index] = {
                                "percentage": round(img_info["match_percentage"], 2),
                                "data": corresponding_object,
                            }
                        seen_urls.add(story_url)  # Mark this URL as seen

            # Convert response_data to a list, sorted by the highest match percentage
            sorted_response = [
                {"percentage": val["percentage"], "data": val["data"]}
                for val in sorted(
                    response_data.values(), key=lambda x: x["percentage"], reverse=True
                )
            ]

            return jsonify(sorted_response)

        except KeyError as e:
            return jsonify({"error": f"Data missing key: {str(e)}"}), 500
        except Exception as e:
            return jsonify({"error": f"Error processing response data: {str(e)}"}), 500

    except requests.RequestException as e:
        return jsonify({"error": f"Error fetching image: {str(e)}"}), 500

    except Exception as e:
        # Clean up the temporary file in case of an error
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        return jsonify({"error": str(e)}), 500

# --------------------------------------------------- # Fetch all data from the JSON file


@app.route("/api/fetchAllData", methods=["GET"])
def fetch_all_data():
    try:
        # Load the data from the JSON file
        with open("csvProcessing/allData.json", "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        # Define the basic headers (without the index field)
        headers = [
            "Story_Date",
            "Story_URL",
            "Headline",
            "What_(Claim)",
            "About_Subject",
            "About_Person",
            "tags",
        ]

        # Find the maximum number of images in any item to dynamically create the headers
        max_images = max(len(item.get("img", [])) for item in data.values())

        # Add headers for the image columns
        image_headers = [f"Featured Image {i+1}" for i in range(max_images)]
        headers.extend(image_headers)

        # Create the CSV rows
        csv_data = []
        csv_data.append(",".join(headers))  # Add headers as the first row

        for item in data.values():
            # Format the row, ensuring we leave empty cells for missing image URLs
            row = [
                str(item.get("Story_Date", "")),
                str(item.get("Story_URL", "")),
                str(item.get("Headline", "")),
                str(item.get("What_(Claim)", "")),
                str(item.get("About_Subject", "")),
                str(item.get("About_Person", "")),
                str(item.get("tags", "")),
            ]

            # Add image URLs to the row, and fill with empty strings for missing images
            images = item.get("img", [])
            row.extend(images + [""] * (max_images - len(images)))

            csv_data.append(",".join(row))

        # Join all the CSV rows into a single string
        csv_string = "\n".join(csv_data)

        # Send CSV data as a response
        return (
            csv_string,
            200,
            {
                "Content-Type": "text/csv",
                "Content-Disposition": "attachment; filename=allData.csv",
            },
        )

    except Exception as e:
        return jsonify({"error": f"Failed to process data: {str(e)}"}), 500


# ---------------------------------------------------

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

    # Make POST request to external API
    try:
        response = requests.post(
            "https://factcheckerbtp.vishvasnews.com/api/appendDataIndividual",
            json=request_data,
            verify=False,
            timeout=3600,
        )
    except requests.exceptions.RequestException as e:
        print(f"Error during external API call: {e}")
        return (
            jsonify(
                {
                    "error": "Failed to forward request to external API",
                    "details": str(e),
                }
            ),
            500,
        )

    return jsonify(result), status_code


def process_csv_data(filepath, expected_columns):
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
            print(
                f"The CSV file is missing the following required columns: {sorted(list(missing_columns))}"
            )
            return

        for row_number, row in enumerate(csv_reader, start=1):
            json_data = {
                "Story_Date": row.get("Story Date"),
                "Story_URL": row.get("Story URL"),
                "Headline": row.get("Headline"),
                "What_(Claim)": row.get("What (Claim)"),
                "About_Subject": row.get("About Subject"),
                "About_Person": row.get("About Person"),
                "tags": row.get("Tags"),
            }

            # Collect all featured image URLs
            image_urls = []
            for i in range(
                1, 16
            ):  # Adjust the range according to the maximum number of images expected
                image_url = row.get(f"Featured Image {i}")
                if image_url:
                    image_urls.append(image_url)

            json_data["img"] = image_urls
            result, status_code = append_story(json_data)
            results.append(result)
            if status_code == 200:
                successful_entries += 1
            elif status_code == 400:
                duplicate_entries += 1
            elif status_code == 500:
                failed_entries += 1
                error_details.append({"row": row_number, "error": result["message"]})

    try:
        with open(filepath, "rb") as file:
            files = {"file": file}
            response = requests.post(
                "https://factcheckerbtp.vishvasnews.com/api/appendDataCSV",
                files=files,
                verify=False,
            )
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error during external API call: {e}")
    finally:
        os.remove(filepath)

    print(
        {
            "message": f"Added {successful_entries} successful entries and discarded {duplicate_entries} duplicates. Failed to append {failed_entries} entries.",
            "results": results,
            "error_details": error_details,
        }
    )


@app.route("/api/appendDataCSV", methods=["POST"])
def append_data_csv():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if not file.filename.endswith(".csv"):
        return jsonify({"error": "Invalid file format, only CSV is allowed"}), 400

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
        "Featured Image 1",  # Adjusted to expect multiple image columns
        "Tags",
    }

    # Process one row to check for errors
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

        first_row = next(csv_reader, None)
        if first_row is None:
            os.remove(filepath)
            return jsonify({"error": "The CSV file is empty"}), 400

        json_data = {
            "Story_Date": first_row.get("Story Date"),
            "Story_URL": first_row.get("Story URL"),
            "Headline": first_row.get("Headline"),
            "What_(Claim)": first_row.get("What (Claim)"),
            "About_Subject": first_row.get("About Subject"),
            "About_Person": first_row.get("About Person"),
            "tags": first_row.get("Tags"),
        }

        # Collect all featured image URLs
        image_urls = []
        for i in range(
            1, 16
        ):  # Adjust the range according to the maximum number of images expected
            image_url = first_row.get(f"Featured Image {i}")
            if image_url:
                image_urls.append(image_url)

        json_data["img"] = image_urls

        result, status_code = append_story(json_data)
        if status_code != 200 and status_code != 400 and status_code != 500:
            os.remove(filepath)
            return (
                jsonify(
                    {"error": "Error in processing the first row", "details": result}
                ),
                400,
            )

    threading.Thread(target=process_csv_data, args=(filepath, expected_columns)).start()

    return (
        jsonify({"message": "Success, your data is being added to the database"}),
        200,
    )


def append_story(request_data):
    file_path = "csvProcessing/allData.json"  # Ensure this path is correct

    # Load the current data from the JSON file or initialize as an empty dictionary if the file does not exist
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            file_data = json.load(file)
    else:
        file_data = {}

    # Check for duplicate entries based on Story_URL
    if any(
        story["Story_URL"] == request_data["Story_URL"] for story in file_data.values()
    ):
        return {"error": "Story URL already exists. No data appended."}, 400

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

    # Handle image downloading and indexing for multiple images
    if "img" in request_data and isinstance(request_data["img"], list):
        image_urls = request_data["img"]
        for idx, image_url in enumerate(image_urls, start=1):
            image_response = requests.get(image_url)
            if image_response.status_code == 200:
                # Open the image from the response
                image = Image.open(BytesIO(image_response.content))

                # Check if the image is PNG and convert to JPG
                if image.format == "PNG":
                    image = image.convert("RGB")
                    image_filename = f"image_{new_index}_{idx}.jpg"
                    image_path = os.path.join("./data", image_filename)
                    image.save(image_path, "JPEG")
                else:
                    image_filename = f"image_{new_index}_{idx}.jpg"
                    image_path = os.path.join("./data", image_filename)
                    with open(image_path, "wb") as f:
                        f.write(image_response.content)

                # Add the image to the index
                try:
                    st.add_images_to_index([image_path])
                except Exception as e:
                    return {"error": f"Failed to index image {idx}: {str(e)}"}, 500
            else:
                return {"error": f"Failed to download image {idx}."}, 500

    # Write the updated data back to the JSON file
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(file_data, file, ensure_ascii=False, indent=4)

    return {"message": "Data appended and images indexed successfully"}, 200


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
    seen_urls = set()  # Set to track seen Story_URLs

    print(type(idx))
    percent = (
        round(
            20 * max(list(scores[:3]) + [model.match_percent(query, origdata[idx[0]])])
        )
        * 5
        if len(idx) > 0
        else None
    )

    origkeys = [origdata[i]["key"] for i in idx]

    for doc_id, score in zip(origkeys[:10], scores[:10]):
        # Access the corresponding document object
        story = data[doc_id]
        story_url = story.get("Story_URL", "")

        # Skip the story if it has already been added
        if story_url in seen_urls:
            continue

        # Add the story URL to the seen list
        seen_urls.add(story_url)

        results.append(
            {
                "percentage": percent,
                "data": story,  # Include the whole news object
            }
        )

    return jsonify(results)


def rank_documents_bm25_bert_trends():
    req = request.json
    query = req.get("query", "")
    log_query("text", query)

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
    percent = round(20 * max(scores[:3])) * 5 if len(idx) > 0 else None

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

    if "Sept" in specified_date_str:
        specified_date_str = specified_date_str.replace("Sept", "Sep")

    try:
        specified_date = datetime.strptime(specified_date_str, "%d %b %Y")
        print(specified_date)
    except ValueError:
        print(f"Invalid date format {specified_date_str}")
        return jsonify({"error": f"Invalid date format {specified_date_str}"}), 400

    start_date = specified_date - timedelta(days=3)
    end_date = specified_date + timedelta(days=3)

    matching_stories = []
    seen_urls = set()  # Set to keep track of already added story URLs

    for story_id, story in data.items():
        story_date_str = story.get("Story_Date", "")
        story_date = parse_story_date(story_date_str)

        if story_date:
            story_date_this_year = replace_year_safe(story_date, specified_date.year)
            if story_date_this_year and start_date <= story_date_this_year <= end_date:
                story_url = story.get("Story_URL", "")

                # Add the story only if its URL has not been added yet
                if story_url and story_url not in seen_urls:
                    matching_stories.append(
                        {
                            "percentage": 100,
                            "data": story,
                            "original_date": story_date,
                        }
                    )
                    seen_urls.add(story_url)  # Mark this URL as seen

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
