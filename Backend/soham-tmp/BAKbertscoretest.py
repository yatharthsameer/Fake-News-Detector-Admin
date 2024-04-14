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
    with open(filepath) as fp:
        data = json.load(fp)
        origdata = []
        for key in sorted(data, key = int):
            val = data[key]
            origdata.append(val.copy())

            val['Story_URL'] = re.sub("\W+", " ", val['Story_URL'][val['Story_URL'].rfind('/', 0, -2) + 1:]).strip()
            for x in val:
                val[x] = re.sub("\s+", " ", val[x].lower()).strip() if val[x] != 'NA' else '' 
                val[x] = re.sub("(quick.)?fact.check\s?\:?\s*", "", val[x]) if val[x].startswith('fact check') or val[x].startswith('fact-check') or val[x].startswith('quick fact check') else val[x]

            tmp = [val[x].strip(': ') for x in ['Story_URL', 'Headline', 'What_(Claim)', 'About_Subject', 'About_Person']]
            docs.append(' | '.join(tmp))
            
            # assert int(key) == len(docs), "Key Mismatch " + key + ' ' + str(len(docs))
    return docs, origdata




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

    
    def clean(self, text:str):
        # print (text)
        return text.lower()
   

    def __call__(self, query, **kwargs):
        return self.rank(query, **kwargs)


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


    def match_percent(self, query, ddict):
        query_vec = self.model.get_sentence_vector(self.clean(query))
        doc_vec = self.model.get_sentence_vector(self.clean(ddict['Headline']))
        return cosine_similarity([query_vec], [doc_vec])[0][0]






################################################################################
################################################################################
class bertscore:
    def __init__(self, docs=[]):
        # print("Loading bertscore model...")
        ts = time()
        self.scorer = BERTScorer(model_type='distilbert-base-multilingual-cased')
        self.docs = [self.clean(x) for x in docs]
        te = time()

        print("BertScore Loading time in s:", round(te-ts, 3))


    def clean(self, text:str):
        return text.lower()


    def __call__(self, query, docs=None, **kwargs):
        return self.rank(query, docs, **kwargs)


    def rank(self, query:str, docs=None, thresh = 0.95, max_out=50, cutoff=0.75):
        ts = time()

        refs = self.docs if docs is None else docs
        cands = [self.clean(query)] * len(refs)

        P, R, F1 = self.scorer.score(cands, refs)
        metric = (F1.numpy() * 100).round(decimals=2)

        idx = metric.argsort()[-max_out:][::-1]
        res = metric[idx]

        idx = idx[(res >= cutoff) & (res >= res[0] * thresh)]
        res = res[(res >= cutoff) & (res >= res[0] * thresh)]
        te = time()

        # print("BERTscore Query time in s:", round(te-ts, 3))

        return idx, res


    def match_percent(self, query, ddict):
        return self.scorer.score([query], [ddict['Headline']])[0]




################################################################################
################################################################################
class ensemble:
    def __init__(self, docs, use_bm25=True, use_ft=True, use_bs=True, use_translation=False):        
        self.use_bm25 = use_bm25
        self.use_ft = use_ft
        self.use_bs = use_bs
        self.use_translation = use_translation

        assert use_bm25 or use_ft or use_bs, "Select at least 1 model"

        self.docs = docs

        if use_bm25:
            self.BM25model = bm25(docs)

        if use_ft:
            self.FTmodel = ftsent(docs) 
        
        if use_bs:
            self.BSmodel = bertscore()
        
        if use_translation:
            self.trans = GoogleTranslator()
            self.transen = GoogleTranslator(source='en', target='hi')


    def __call__(self, query, **kwargs):
        return self.rank(query, **kwargs)

    def translate(self, text):
        assert self.use_translation, "Translator not initialized"

        # if english
        enchars = re.sub("[^A-Za-z0-9]", "", text)
        # print(enchars)
        if len(enchars) >= 0.6 * len(text):
            print("En -> Hi")
            return self.transen.translate(text)

        print("Auto -> En")
        return self.trans.translate(text)
    

    def rank(self, query, thresh=0.9, cutoff=0.6, max_out=50, k = 10):
        ts = time()
        
        results = []
        indices = set()

        transquery = None
        if self.use_translation:
            try:
                transquery = self.translate(query)
                print(transquery)
            except Exception as args:
                print("TRANSLATE ERROR:", args)


        if self.use_bm25:
            bm25idx, bm25res = self.BM25model.rank(query)
            indices |= set(bm25idx)
            results.append(bm25idx)
            
            if not transquery is None:
                bm25idx2, bm25res2 = self.BM25model.rank(transquery, thresh=0.9)
                indices |= set(bm25idx2)
                # results.append(bm25idx2)


        if self.use_ft:
            ftidx, ftres = self.FTmodel.rank(query)
            indices |= set(ftidx)
            results.append(ftidx)

            if not transquery is None:
                ftidx2, ftres2 = self.FTmodel.rank(transquery, cutoff=0.9)
                indices |= set(ftidx2)
                # results.append(ftidx2)


        if self.use_bs:
            indices = np.array(list(indices))
            tmpdocs = [self.docs[i] for i in indices]
            print("Total #docs for running bertscore:", len(indices))

            tmpidx, bsres = self.BSmodel.rank(query, tmpdocs)
            bsidx = indices[tmpidx]
            results.append(bsidx)


        # Reciprocal Rank Fusion
        docrrf = [0] * len(self.docs)
        for num, idx in enumerate(results):
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

    def match_percent(self, query, ddict):
        per = self.FTmodel.match_percent(query, ddict)

        if self.use_translation:
            try:
                qt = self.translate(query)
                tmp = self.FTmodel.match_percent(qt, ddict)
                per = max(per, tmp)
            except Exception as args:
                print("TRANSLATE ERROR:", args)

        return round(per, 4)

        # return self.BSmodel.match_percent(query, ddict)






################################################################################
################################################################################
if __name__ == '__main__':
    ########################################
    # #### Minimal Example:
    # docs, h = load_data()
    # model = ensemble(docs)
    
    # idx, res = model(query)


    ########################################
    # QUERY = 'anushka sharma married kohli'
    # QUERY = ['rahul gandhi drinking', 'anushka sharma', 'priyanka chopra', 'priyanka gandhi', 'priyankaa chopra', 'priyankaa gandhi', 'priyankaa gandhi posted', 'virat koli']
    QUERY = ['rahul gandhi', 'rahul gandhi drinking']
    # with open('queries_test.txt') as fp:
    #     QUERY = fp.read().splitlines()


    docs, orig = load_data()
    model = ensemble(docs)

    for num, query in enumerate(QUERY):
        print('\n' + "#"*100)
        # print("#"*40 + " BM25 " + "#"*40)
        print("QUERY", num, query)
        
        idx, res = model.rank(query, cutoff=0.5, thresh=0.85)

        for i, v in zip(idx[:10], res[:10]): 
            print(" --> ", v, i, docs[i])
            print(" +-> ", orig[i]['Headline'])
            print()

        percent = max(res[0], model.match_percent(query, orig[idx[0]])) if len(idx) > 0 else None
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