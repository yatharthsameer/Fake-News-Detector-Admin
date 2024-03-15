import json
import pandas as pd
import torch
from transformers import AutoModel, AutoTokenizer
import numpy as np
import logging

# Setup basic configuration for logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load the JSON file
json_file_path = "csvProcessing/allData.json"  # Update path as needed
logging.info(f"Loading data from {json_file_path}")
try:
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
except Exception as e:
    logging.error(f"Failed to load data from {json_file_path}: {e}")
    raise

# Adjusted to iterate through data.items() for the new dictionary structure
texts, ids = [], []  # Keep track of IDs for reference
for id, item in data.items():
    if all(key in item for key in ["Headline", "What_(Claim)", "About_Subject"]):
        concatenated_text = (
            f"{item['Headline']} {item['What_(Claim)']} {item['About_Subject']}"
        )
        texts.append(concatenated_text)
        ids.append(id)
    else:
        logging.warning(f"Missing required fields in item ID {id}")

logging.info("Text concatenation complete. Proceeding to generate embeddings.")

# Load IndicBERT model and tokenizer
logging.info("Loading IndicBERT model and tokenizer.")
tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-bert")
model = AutoModel.from_pretrained("ai4bharat/indic-bert")


def get_embedding(text):
    """Generate embeddings for the given text using IndicBERT."""
    inputs = tokenizer(
        text, return_tensors="pt", padding=True, truncation=True, max_length=512
    )
    with torch.no_grad():
        outputs = model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()


# Generate embeddings for all texts
logging.info("Generating embeddings for all texts.")
try:
    embeddings = [get_embedding(text) for text in texts]
    embeddings = np.vstack(embeddings)  # Stack embeddings to form a matrix
except Exception as e:
    logging.error(f"Failed to generate embeddings: {e}")
    raise

# Convert embeddings to a DataFrame for easy CSV storage
embeddings_df = pd.DataFrame(embeddings)
embeddings_df["ID"] = ids  # Add the IDs column for reference
embeddings_df["Text"] = texts  # Add the original texts for reference

csv_output_path = "indicbert_text_embeddings.csv"
logging.info(f"Saving embeddings to {csv_output_path}.")
try:
    embeddings_df.to_csv(csv_output_path, index=False)
    logging.info("Embeddings successfully saved.")
except Exception as e:
    logging.error(f"Failed to save embeddings: {e}")
