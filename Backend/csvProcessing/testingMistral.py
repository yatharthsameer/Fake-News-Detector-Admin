# from transformers import AutoModelForCausalLM, AutoTokenizer


# model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
# tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")

# messages = [
#     {"role": "user", "content": "What is your favourite condiment?"},
#     {
#         "role": "assistant",
#         "content": "Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!",
#     },
#     {"role": "user", "content": "Do you have mayonnaise recipes?"},
# ]

# encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")

# model_inputs = encodeds

# generated_ids = model.generate(model_inputs, max_new_tokens=1000, do_sample=True)
# decoded = tokenizer.batch_decode(generated_ids)
# print(decoded[0])
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Set device to CPU

# Initialize the model and tokenizer with specific arguments for reduced memory usage
model = AutoModelForCausalLM.from_pretrained(
    "LsTam/Mistral-7B-Instruct-v0.2-8bit",
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    use_flash_attention_2=True,
    load_in_8bit=True
)
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
tokenizer.padding_side = "left"
# if not tokenizer.pad_token_id:
tokenizer.pad_token_id = tokenizer.eos_token_id
tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = tokenizer.eos_token_id
# Your chat history/messages
messages = [
    {"role": "user", "content": "What is your favourite condiment?"},
    {
        "role": "assistant",
        "content": "Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!",
    },
    {"role": "user", "content": "Do you have mayonnaise recipes?"},
]

# Tokenize and format the conversation using the chat history template
encodeds = tokenizer.apply_chat_template(messages, return_tensors="pt")


# Move the model inputs to the CPU
model_inputs = encodeds

# Also ensure the model is using the CPU

# Generate a response from the model
generated_ids = model.generate(model_inputs, max_new_tokens=1000, do_sample=True)

# Decode the generated ids to get the text
decoded = tokenizer.batch_decode(generated_ids)

# Print the generated text
print(decoded[0])
