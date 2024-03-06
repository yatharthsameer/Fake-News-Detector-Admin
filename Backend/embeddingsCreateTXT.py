import json
import pandas as pd
import torch
from transformers import AutoModel, AutoTokenizer
import numpy as np

# Load the JSON file
with open("data.json", "r") as file:
    data = json.load(file)

# Extract the relevant text data from the JSON objects
# Concatenate the "Headline" and "What_(Claim)" for a richer representation
texts = [
    item["Headline"] + " " + item["What_(Claim)"] + " " + item["About_Subject"]
    for item in data
]

# Load IndicBERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-bert")
model = AutoModel.from_pretrained("ai4bharat/indic-bert")


def get_embedding(text):
    """Generate embeddings for the given text using IndicBERT."""
    print(text)
    inputs = tokenizer(
        text, return_tensors="pt", padding=True, truncation=True, max_length=512
    )
    with torch.no_grad():
        outputs = model(**inputs)
        # Using mean pooling to get a fixed size embedding vector
        return outputs.last_hidden_state.mean(dim=1).numpy()


# Generate embeddings for all texts
embeddings = [get_embedding(text) for text in texts]

embeddings = np.vstack(embeddings)  # Stack embeddings to form a matrix

# Convert embeddings to a DataFrame for easy CSV storage
embeddings_df = pd.DataFrame(embeddings)

# Add the original texts for reference
embeddings_df["Text"] = texts

# Save the embeddings to a CSV file
embeddings_df.to_csv("indicbert_text_embeddings.csv", index=False)
