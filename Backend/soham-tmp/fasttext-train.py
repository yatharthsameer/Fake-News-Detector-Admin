import fasttext
from BERTClasses import load_data
import os

if not os.path.exists('fasttext-tmp/'):
    os.makedirs('fasttext-tmp/')


docs, orig = load_data("../csvProcessing/allData.json")
with open('fasttext-tmp/data.txt', 'w') as fo:
    fo.write("\n".join(docs))


model = fasttext.train_unsupervised('fasttext-tmp/data.txt', minCount=2, wordNgrams=3, epoch=50, dim=200, neg=10)
model.save_model("fasttext-tmp/model.bin")
