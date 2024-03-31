import os
# os.environ['CUDA_VISIBLE_DEVICES'] = ""

from bert_score import BERTScorer
from rank_bm25 import BM25Plus
import fasttext
from sklearn.metrics.pairwise import cosine_similarity 
from deep_translator import GoogleTranslator
import json
from time import time
import re
import spacy
import numpy as np
from multiprocessing import Pool, Process



################################################################################
################################################################################
# for SPACY
NUM_PROCS = 16


def load_data(filepath='../csvProcessing/allData.json'):
    docs = []
    head = []
    with open(filepath) as fp:
        data = json.load(fp)
        for key in sorted(data, key = int):
            val = data[key]

            val['Story_URL'] = re.sub("\W+", " ", val['Story_URL'][val['Story_URL'].rfind('/', 0, -2) + 1:]).strip()
            for x in val:
                val[x] = re.sub("\s+", " ", val[x].lower()).strip() if val[x] != 'NA' else '' 
                val[x] = re.sub("(quick.)?fact.check\s?\:?\s*", "", val[x]) if val[x].startswith('fact check') or val[x].startswith('fact-check') or val[x].startswith('quick fact check') else val[x]

            tmp = [val[x].strip(': ') for x in ['Story_URL', 'Headline', 'What_(Claim)', 'About_Subject', 'About_Person']]
            docs.append(' | '.join(tmp))
            head.append(val['Headline'])

            # assert int(key) == len(docs), "Key Mismatch " + key + ' ' + str(len(docs))
    return docs, head




################################################################################
################################################################################
class bm25:
    def __init__(self, docs, use_lemma=True):
        self.use_lemma = use_lemma
        # print("Loading BM25 model...")
        ts = time()
        self.nlp = spacy.load('en_core_web_sm')
        self.docs = [self.clean(x) for x in docs]
        # tokenized_corpus = [self.tokenize(x) for x in docs]
        with Pool(NUM_PROCS) as p:
            tokenized_corpus = p.map(self.tokenize, docs)

        self.scorer = BM25Plus(tokenized_corpus)
        te = time()

        print("BM25 Loading time in s:", round(te-ts, 3))

    def __call__(self, query, **kwargs):
        return self.rank(query, **kwargs)
        

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

        idx = idx[res >= res[0] * thresh]
        res = res[res >= res[0] * thresh]
        te = time()

        # print("BM25 Query time in s:", round(te-ts, 3))
        return idx, res


################################################################################
################################################################################
class ftsent:
    def __init__(self, docs, model_path='fasttext-tmp/model.bin'):
        # print("Loading FT-sent model...")
        ts = time()
        self.model = fasttext.load_model(model_path)

        self.doc_vecs = [self.model.get_sentence_vector(x) for x in docs]
        te = time()

        print("FT-sent Loading time in s:", round(te-ts, 3))

    
    def __call__(self, query, **kwargs):
        return self.rank(query, **kwargs)
         

    def clean(self, text:str):
        # print (text)
        return text.lower()
   
    def rank(self, query:str, thresh = 0.95, cutoff=0.8, max_out=50):
        ts = time()
        query_vec = self.model.get_sentence_vector(self.clean(query))
        cos_sim = cosine_similarity([query_vec], self.doc_vecs)

        metric = (cos_sim[0] * 100).round(decimals=2)

        idx = metric.argsort()[-max_out:][::-1]
        res = metric[idx]

        idx = idx[(res >= cutoff) & (res >= res[0] * thresh)]
        res = res[(res >= cutoff) & (res >= res[0] * thresh)]
        
        te = time()
        
        # print("FT-sent Query time in s:", round(te-ts, 3))
        return idx, res


    def match_percent(self, query, doc):
        query_vec = self.model.get_sentence_vector(self.clean(query))
        doc_vec = self.model.get_sentence_vector(self.clean(doc))
        
        return cosine_similarity([query_vec], [doc_vec])[0][0]






################################################################################
################################################################################
class bertscore:
    def __init__(self, docs, use_bm25=True, use_ftsent=True):
        self.use_bm25 = use_bm25
        self.use_ftsent = use_ftsent
            
        if use_bm25:
            self.bm25model = bm25(docs)

        if use_ftsent:
            self.ftsentmodel = ftsent(docs) 


        # print("Loading bertscore model...")
        ts = time()
        self.scorer = BERTScorer(model_type='distilbert-base-multilingual-cased')
        self.docs = [self.clean(x) for x in docs]
        te = time()

        print("BertScore Loading time in s:", round(te-ts, 3))


       
    def clean(self, text:str):
        return text.lower()

    def __call__(self, query, **kwargs):
        return self.rank(query, **kwargs)
    
    def rank(self, query:str, thresh = 0.95, max_out=50, cutoff=0.75, return_aux=False):
        ts = time()

        indices = set()
        aux_out = []
        if self.use_bm25:
            bm25idx, bm25res = self.bm25model.rank(query)
            indices |= set(bm25idx)    
            # print("#docs from BM25:", len(bm25idx))
            if return_aux:
                aux_out.append((bm25idx, bm25res))

                    
        if self.use_ftsent:
            ftidx, ftres = self.ftsentmodel.rank(query)
            indices |= set(ftidx)
            # print("#docs from FT-sent:", len(ftidx))
            if return_aux:
                aux_out.append((ftidx, ftres))

        
        if self.use_bm25 or self.use_ftsent:
            indices = np.array(list(indices))
            refs = [self.docs[i] for i in indices]
            print("Total #docs for running bertscore:", len(indices))
        else:
            refs = self.docs
            

        cands = [self.clean(query)] * len(refs)

        P, R, F1 = self.scorer.score(cands, refs)
        metric = (F1.numpy() * 100).round(decimals=2)

        idx = metric.argsort()[-max_out:][::-1]
        res = metric[idx]

        idx = idx[(res >= cutoff) & (res >= res[0] * thresh)]
        res = res[(res >= cutoff) & (res >= res[0] * thresh)]
        te = time()

        # print("BERTscore Query time in s:", round(te-ts, 3))

        if self.use_bm25 or self.use_ftsent:
            idx = indices[idx]
        
        if return_aux:
            return [(idx, res)] + aux_out
        return idx, res

    def match_percent(self, query, doc):
        return self.scorer.score([query], [doc])[0]




################################################################################
################################################################################
class ensemble:
    def __init__(self, docs, use_translation=False):
        self.BS = bertscore(docs)
        self.use_translation = use_translation
        if use_translation:
            self.trans = GoogleTranslator()
            self.entrans = GoogleTranslator(source='en', target='hi')

    def __call__(self, query, **kwargs):
        return self.rank(query, **kwargs)

    def translate(self, text):
        return text
    
    def rank(self, query, thresh=0.9, cutoff=0.5, max_out=50, k = 10):
        ts = time()
        
        results = self.BS(query, return_aux=True)

        docrrf = [0] * len(self.BS.docs)
        for num, (idx, res) in enumerate(results):
            print("len%d"%num, len(idx), end = '\t')
            for rank, i in enumerate(idx):
                docrrf[i] += 1 / (k + rank + 1)
        
        
        metric = np.array(docrrf) * k / len(results)
        idx = metric.argsort()[-max_out:][::-1]
        res = metric[idx].round(4)

        idx = idx[(res >= cutoff) & (res >= res[0] * thresh)]
        res = res[(res >= cutoff) & (res >= res[0] * thresh)]

        te = time()
        print("\nQuery time in s:", round(te-ts, 3))
        return idx, res

    def match_percent(self, query, doc):
        return self.BS.ftsentmodel.match_percent(query, doc)
        # return self.BS.match_percent(query, doc)








################################################################################
################################################################################
if __name__ == '__main__':
    ########################################
    # #### Minimal Example:
    # docs, hs = load_data()
    # model = ensemble(docs)
    
    # idx, res = model(query)


    ########################################
    # QUERY = 'anushka sharma married kohli'
    # QUERY = ['rahul gandhi drinking', 'anushka sharma', 'priyanka chopra', 'priyanka gandhi', 'priyankaa chopra', 'priyankaa gandhi', 'priyankaa gandhi posted', 'virat koli']
    # QUERY = ['rahul gandhi drinking']
    with open('queries_test.txt') as fp:
        QUERY = fp.read().splitlines()


    docs, heads = load_data()
    model = ensemble(docs)

    for num, query in enumerate(QUERY):
        print('\n' + "#"*100)
        # print("#"*40 + " BM25 " + "#"*40)
        print("QUERY", num, query)
        
        idx, res = model(query)
        for i, v in zip(idx[:10], res[:10]): 
            print(" --> ", v, i, docs[i])
            print(" +-> ", v, i, heads[i])
            print()

        percent = model.match_percent(query, heads[idx[0]]) if len(idx) > 0 else None
        print("Percent Match", percent)


    '''
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
        
        idx, res = model.ftsentmodel(query)
        for i, v in zip(idx[:10], res[:10]): 
            print(" --> ", v, i, docs[i])

        print("\n")
        print("#"*40 + " BM25 + BERTSCORE " + "#"*40)
        print("QUERY:", query)

        # Main running method
        idx, res = model(query, max_out=5)
        for i, v in zip(idx[:10], res[:10]): 
            print(" --> ", v, i, docs[i])

    '''