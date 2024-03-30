import token
from bert_score import BERTScorer
from rank_bm25 import BM25Plus
import fasttext
from sklearn.metrics.pairwise import cosine_similarity 
import json
from time import time
import os
import re
import spacy
import numpy as np

os.environ['CUDA_VISIBLE_DEVICES'] = ''



class bm25:
    def __init__(self, docs, use_lemma=True):
        self.use_lemma = use_lemma
        print("Loading BM25 model...")
        ts = time()
        self.nlp = spacy.load('en_core_web_sm')
        # self.docs = [self.clean(x) for x in docs]
        tokenized_corpus = [self.tokenize(x) for x in docs]
        self.scorer = BM25Plus(tokenized_corpus)
        te = time()

        print("Loading time in s:", round(te-ts, 3))
        

    def clean(self, text:str):
        # print (text)
        return text.lower()

    def tokenize(self, text:str):
        if self.use_lemma:
            return [x.lemma_ for x in self.nlp(text)]    
        
        return text.split()
    
    def rank(self, query:str, thresh=0.8, max_out=50):
        ts = time()
        
        tokenized_query = self.tokenize(self.clean(query))
        scores = self.scorer.get_scores(tokenized_query)
        metric = scores.round(decimals=2)

        idx = metric.argsort()[-max_out:][::-1]
        res = metric[idx]
        res = res[res >= res[0] * thresh]
        te = time()

        print("BM25 Query time in s:", round(te-ts, 3))
        return idx, res



class ftsent:
    def __init__(self, docs, model_path='fasttext-tmp/model.bin'):
        print("Loading FT-sent model...")
        ts = time()
        self.model = fasttext.load_model(model_path)

        self.doc_vecs = [self.model.get_sentence_vector(x) for x in docs]
        te = time()

        print("Loading time in s:", round(te-ts, 3))
        

    def clean(self, text:str):
        # print (text)
        return text.lower()
   
    def rank(self, query:str, thresh = 0.8, max_out=50):
        ts = time()
        query_vec = self.model.get_sentence_vector(self.clean(query))
        cos_sim = cosine_similarity([query_vec], self.doc_vecs)

        metric = (cos_sim[0] * 100).round(decimals=2)

        idx = metric.argsort()[-max_out:][::-1]
        res = metric[idx]
        res = res[res >= res[0] * thresh]
        te = time()
        
        print("FT-sent Query time in s:", round(te-ts, 3))
        return idx, res







class bertscore:
    def __init__(self, docs, cutoff=0.5, use_bm25=True, use_ftsent=True):
        self.use_bm25 = use_bm25
        self.use_ftsent = use_ftsent
        self.cutoff = cutoff
            
        if use_bm25:
            self.bm25model = bm25(docs)

        if use_ftsent:
            self.ftsentmodel = ftsent(docs) 


        print("Loading bertscore model...")
        ts = time()
        self.scorer = BERTScorer(model_type='distilbert-base-multilingual-cased')
        self.docs = [self.clean(x) for x in docs]
        te = time()

        print("Loading time in s:", round(te-ts, 3))


       
    def clean(self, text:str):
        return text.lower()
    
    def rank(self, query:str, thresh = 0.95, max_out=10):
        ts = time()

        indices = set()
        if self.use_bm25:
            bm25idx, bm25res = self.bm25model.rank(query)
            indices |= set(bm25idx)    
            print("#docs from BM25:", len(bm25idx))
                    
        if self.use_ftsent:
            ftidx, ftres = self.ftsentmodel.rank(query)
            indices |= set(ftidx)
            print("#docs from FT-sent:", len(ftidx))
        
        if self.use_bm25 or self.use_ftsent:
            indices = np.array(list(indices))
            refs = [self.docs[i] for i in indices]
            print("Total #docs for running bertscore:", len(indices))
        else:
            refs = self.docs
            

        cands = [self.clean(query)] * len(refs)

        P, R, F1 = self.scorer.score(cands, refs)
        metric = (P.numpy() * 100).round(decimals=2)

        idx = metric.argsort()[-max_out:][::-1]
        res = metric[idx]
        res = res[res >= res[0] * thresh] if res[0] >= self.cutoff else []
        te = time()

        if self.use_bm25 or self.use_ftsent:
            idx = indices[idx]
        
        print("BERTscore Query time in s:", round(te-ts, 3))
        return idx, res



def load_data(filepath='../csvProcessing/allData.json'):
    docs = []
    with open(filepath) as fp:
        data = json.load(fp)
        for key, val in data.items():
            val['Story_URL'] = re.sub("\W+", " ", val['Story_URL'][val['Story_URL'].rfind('/', 0, -2) + 1:]).strip()
            for x in val:
                val[x] = re.sub("\s+", " ", val[x].lower()).strip() if val[x] != 'NA' else '' 
                val[x] = re.sub("(quick.)?fact.check\s?\:?\s*", "", val[x]) if val[x].startswith('fact check') or val[x].startswith('fact-check') or val[x].startswith('quick fact check') else val[x]

            tmp = [val[x].strip(': ') for x in ['Story_URL', 'Headline', 'What_(Claim)', 'About_Subject', 'About_Person']]
            docs.append(' | '.join(tmp))
    return docs


if __name__ == '__main__':
    ########################################
    # #### Minimal Example:
    # docs = load_data()
    # model = bertscore(docs)
    
    # idx, res = model.rank(query)


    ########################################
    # QUERY = 'anushka sharma married kohli'
    # QUERY = ['rahul gandhi drinking', 'anushka sharma', 'priyanka chopra', 'priyanka gandhi', 'priyankaa chopra', 'priyankaa gandhi', 'priyankaa gandhi posted', 'virat koli']
    QUERY = ['rahul gandhi drinking']

    docs = load_data()
    model = bertscore(docs)

    for query in QUERY:
        print("\n")
        print("#"*100)
        print("#"*40 + " BM25 " + "#"*40)
        print("QUERY:", query)
        
        idx, res = model.bm25model.rank(query)
        for i, v in zip(idx[:10], res[:10]): 
            print(" --> ", v, i, docs[i])

        print("\n")
        print("#"*40 + " FT-sent " + "#"*40)
        print("QUERY:", query)
        
        idx, res = model.ftsentmodel.rank(query)
        for i, v in zip(idx[:10], res[:10]): 
            print(" --> ", v, i, docs[i])

        print("\n")
        print("#"*40 + " BM25 + BERTSCORE " + "#"*40)
        print("QUERY:", query)

        # Main running method
        idx, res = model.rank(query)
        for i, v in zip(idx[:10], res[:10]): 
            print(" --> ", v, i, docs[i])
