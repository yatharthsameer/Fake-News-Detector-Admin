from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


MODEL_PATH = 'mistralai/Mistral-7B-Instruct-v0.2'
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
model.bfloat16()
tokenizer.padding_side = "left"
# if not tokenizer.pad_token_id:
tokenizer.pad_token_id = tokenizer.eos_token_id
tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = tokenizer.eos_token_id


rawdata = ["hello world"]
# data_loader = data_utils.DataLoader(rawdata, )
batch = rawdata
# for idx, batch in enumerate(tqdm(rawdata, ncols=50)):
batchdata = tokenizer(batch, return_tensors="pt", padding=True, truncation=True)
inp = batchdata.input_ids
attn = batchdata.attention_mask
outputs = model.generate(
    inp,
    attention_mask=attn,
    max_new_tokens=50,
    pad_token_id=tokenizer.pad_token_id,
)
