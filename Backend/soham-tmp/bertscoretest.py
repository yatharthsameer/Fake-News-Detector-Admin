import token
from bert_score import BERTScorer
from rank_bm25 import BM25Plus
import json
from time import time
import os
import spacy

os.environ['CUDA_VISIBLE_DEVICES'] = ''



class bm25:
    def __init__(self, docs, use_lemma=True):
        self.use_lemma = use_lemma
        print("Loading BM25 model...")
        ts = time()
        self.nlp = spacy.load('en_core_web_sm')
        self.docs = [self.clean(x) for x in docs]
        tokenized_corpus = [self.tokenize(x) for x in self.docs]
        self.scorer = BM25Plus(tokenized_corpus)
        te = time()

        print("Loading time in s:", round(te-ts, 3))
        

    def clean(self, text:str):
        # print (text)
        if text.startswith('fact check: '):
            text = text[12:]

        return text.lower()

    def tokenize(self, text:str):
        if self.use_lemma:
            return [x.lemma_ for x in self.nlp(text)]    
        
        return text.split()
    
    def rank(self, query:str, num_out=100):
        ts = time()
        
        tokenized_query = self.tokenize(self.clean(query))
        scores = self.scorer.get_scores(tokenized_query)
        metric = scores.round(decimals=2)

        idx = metric.argsort()[-num_out:][::-1]
        res = metric[idx]
        te = time()

        print("BM25 Query time in s:", round(te-ts, 3))
        return idx, res




class bertscore:
    def __init__(self, docs, use_bm25=True, bm25_thresh=0.75):
        self.use_bm25 = use_bm25
        if use_bm25:
            self.bm25model = bm25(docs)
            self.bm25_thresh = bm25_thresh

        print("Loading bertscore model...")
        ts = time()
        self.scorer = BERTScorer(model_type='distilbert-base-multilingual-cased')
        self.docs = [self.clean(x) for x in docs]
        te = time()

        print("Loading time in s:", round(te-ts, 3))
       
    def clean(self, text:str):
        return text.lower()
    
    def rank(self, query:str, num_out=10):
        ts = time()

        if self.use_bm25:
            bm25idx, bm25res = self.bm25model.rank(query)
            refs = [self.docs[i] for i, val in zip(bm25idx, bm25res) if val > bm25res[0] * self.bm25_thresh]
            print("#docs from BM25:", len(refs))
        else:
            refs = self.docs

        cands = [self.clean(query)] * len(refs)

        P, R, F1 = self.scorer.score(cands, refs)
        metric = (P.numpy() * 100).round(decimals=2)

        idx = metric.argsort()[-num_out:][::-1]
        res = metric[idx]
        te = time()

        if self.use_bm25:
            idx = bm25idx[idx]
        
        print("BERTscore Query time in s:", round(te-ts, 3))
        return idx, res



if __name__ == '__main__':
    # QUERY = 'anushka sharma married kohli'
    QUERY = ['rahul gandhi', 'anushka sharma', 'priyanka chopra', 'priyanka gandhi', 'vir koli']
    
    with open('../csvProcessing/allData.json') as fp:
        data = json.load(fp)
        docs = [' | '.join([val[x] if val[x] != 'NA' else '' for x in ['Headline', 'What_(Claim)', 'About_Subject', 'About_Person']]) for key, val in data.items()]
        # docs = docs[:1000]

    # model = bm25(docs)
    model = bertscore(docs)

    print("\n")
    print("#"*100)
    for query in QUERY:
        print(query)
        idx, res = model.bm25model.rank(query)
        for x in idx[:10]: 
            print(docs[x])

        print("\n")
        print("#"*100)
        idx, res = model.rank(query)
        for x in idx[:10]: 
            print(docs[x])

