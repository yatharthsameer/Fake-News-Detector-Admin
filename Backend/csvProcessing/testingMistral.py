from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Set the model path
MODEL_PATH = "mistralai/Mistral-7B-Instruct-v0.2"

# Initialize the tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

# Initialize the model and convert it to use bfloat16 for memory efficiency
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH).to(torch.bfloat16())

# Adjust tokenizer padding and pad token settings
tokenizer.padding_side = "left"
# Use EOS token as pad token if a specific pad token is not set
tokenizer.pad_token_id = tokenizer.eos_token_id
tokenizer.pad_token = tokenizer.eos_token
# Ensure the model's pad token id is set correctly
model.config.pad_token_id = tokenizer.eos_token_id

# Example conversation/messages
messages = [
    {"role": "user", "content": "What is your favourite condiment?"},
    {
        "role": "assistant",
        "content": "Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!",
    },
    {"role": "user", "content": "Do you have mayonnaise recipes?"},
]

# Tokenize and format the conversation using the chat history template
encoded_inputs = tokenizer(messages, return_tensors="pt", padding=True)

# Move the model inputs to the CPU
model_inputs = encoded_inputs.to("cpu")

# Generate a response from the model
generated_ids = model.generate(**model_inputs, max_new_tokens=1000, do_sample=True)

# Decode the generated ids to get the text
decoded = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

# Print the generated text
print(decoded[0])
