import fasttext
from BERTClasses import load_data
import os

if not os.path.exists('fasttext-tmp/'):
    os.makedirs('fasttext-tmp/')


docs = load_data()
with open('fasttext-tmp/data.txt', 'w') as fo:
    fo.write("\n".join(docs))


model = fasttext.train_unsupervised('fasttext-tmp/data.txt', minCount=2, wordNgrams=2, epoch=10)
model.save_model("fasttext-tmp/model.bin")
