import os

os.environ['CUDA_VISIBLE_DEVICES'] = "2"

from bert_score import BERTScorer
from rank_bm25 import BM25Plus
import fasttext
from sklearn.metrics.pairwise import cosine_similarity
# from deep_translator import GoogleTranslator
import json
from time import time
import re
from collections import defaultdict
import spacy
import numpy as np
from multiprocessing import Pool, Process
from datetime import datetime

from IndicTrans2.inference.engine import Model as IT2Model



################################################################################
################################################################################
# for SPACY; Use 1 if there are problems with the multiproccessing library
NUM_PROCS = 16


def load_data(filepath="csvProcessing/allData.json"):
    docs = []
    with open(filepath) as fp:
        data = json.load(fp)
        origdata = []
        for key in sorted(data, key=int):
            val = data[key]
            val['key'] = key
            

            try:
                val['Story_Date'] = datetime.strptime(re.sub("(st|nd|rd|th)\s+", " ", val['Story_Date']), "%d %b %Y")
            except ValueError as args:
                print("Time error:", args)
                continue

            origdata.append(val.copy())
            del val['Story_Date']
            del val['key']


            val["Story_URL"] = re.sub(
                "\W+", " ", val["Story_URL"][val["Story_URL"].rfind("/", 0, -2) + 1 :]
            ).strip()
            for x in val:
                val[x] = (
                    re.sub("\s+", " ", val[x].lower()).strip() if val[x] and val[x].lower() not in ["na", "n/a"]   else ""
                )

                val[x] = (
                    re.sub("(quick.)?fact.check\s?\:?\s*", "", val[x])
                    if val[x].startswith("fact check")
                    or val[x].startswith("fact-check")
                    or val[x].startswith("quick fact check")
                    else val[x]
                )

            tmp = [
                val[x].strip(": ")
                for x in [
                    "Story_URL",
                    "Headline",
                    "What_(Claim)",
                    "About_Subject",
                    "About_Person",
                    "tags"
                ]
            ]
            docs.append(" | ".join(tmp))

            # assert int(key) == len(docs), "Key Mismatch " + key + ' ' + str(len(docs))
    return docs, origdata





################################################################################
################################################################################
class bm25:
    def __init__(self, docs, use_lemma=True):
        self.use_lemma = use_lemma
        # print("Loading BM25 model...")
        ts = time()
        self.nlp = spacy.load("en_core_web_sm")
        self.docs = [self.clean(x) for x in docs]

        if NUM_PROCS > 1:
            with Pool(NUM_PROCS) as p:
                tokenized_corpus = p.map(self.tokenize, docs)
        else:
            tokenized_corpus = map(self.tokenize, docs)

        self.scorer = BM25Plus(tokenized_corpus)
        te = time()

        print("BM25 Loading time in s:", round(te - ts, 3))

    def __call__(self, query, **kwargs):
        return self.rank(query, **kwargs)

    def add_docs(self, docs):
        tmp = [self.clean(x) for x in docs]
        self.docs.extend(tmp)
        tokenized_corpus = map(self.tokenize, tmp)
        self.scorer = BM25Plus(tokenized_corpus)



    def clean(self, text: str):
        # print (text)
        return text.lower()

    def tokenize(self, text: str):
        if self.use_lemma:
            return [x.lemma_.lower() for x in self.nlp(text)]

        return text.split()

    def rank(self, query: str, thresh=0.6, max_out=25):
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
    def __init__(self, docs, model_path="fasttext-tmp/model.bin"):
        # print("Loading FT-sent model...")
        ts = time()
        self.model = fasttext.load_model(model_path)
        self.doc_vecs = [self.model.get_sentence_vector(x) for x in docs]
        te = time()

        print("FT-sent Loading time in s:", round(te - ts, 3))

    def clean(self, text: str):
        # print (text)
        return text.lower()

    def __call__(self, query, **kwargs):
        return self.rank(query, **kwargs)
    
    def add_docs(self, docs):
        self.doc_vecs.extend([self.model.get_sentence_vector(x) for x in docs])


    def rank(self, query: str, thresh=0.85, cutoff=0.6, max_out=25):
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
        doc_vec = self.model.get_sentence_vector(self.clean(ddict["Headline"]))
        return cosine_similarity([query_vec], [doc_vec])[0][0]




################################################################################
################################################################################
class bertscore:
    def __init__(self, docs=[]):
        # print("Loading bertscore model...")
        ts = time()
        self.scorer = BERTScorer(model_type="distilbert-base-multilingual-cased")
        # self.scorer = BERTScorer(model_type="xlm-roberta-large")
        # self.scorer = BERTScorer(model_type="microsoft/mdeberta-v3-base")
        self.docs = [self.clean(x) for x in docs]
        te = time()

        print("BertScore Loading time in s:", round(te - ts, 3))

    def clean(self, text: str):
        return text.lower()

    def __call__(self, query, docs=None, **kwargs):
        return self.rank(query, docs, **kwargs)
    
    def add_docs(self, docs):
        self.docs.extend([self.clean(x) for x in docs])


    def rank(self, query: str, docs=None, thresh=0.8, cutoff=0.6, max_out=25):
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
        return self.scorer.score([query], [ddict["Headline"]])[0]







################################################################################
################################################################################
class ensemble:
    def __init__(
        self, docs, use_bm25=True, use_ft=True, use_bs=True, use_translation=False, use_date_level=1, origdocs = None
    ):
        self.use_bm25 = use_bm25
        self.use_ft = use_ft
        self.use_bs = use_bs
        self.use_translation = use_translation
        self.use_date_level = use_date_level
        self.origdocs = origdocs
        # self.sort_date = sort_date

        assert use_bm25 or use_ft or use_bs, "Select at least 1 model"

        assert not use_date_level or origdocs, "Need original docs if using date"
        # assert not sort_date or origdocs, "Need original docs if using date"

        self.docs = docs

        if use_bm25:
            # print(docs[:5], type(docs[:5]))
            self.BM25model = bm25(docs)
            # (docs -> sort)

        if use_ft:
            self.FTmodel = ftsent(docs)
            # (docs -> sort)

        if use_bs:
            self.BSmodel = bertscore()
            # (docs -> sort) - > threshold

        if use_translation:
            self.trans = IT2Model("IndicTrans2/indic-en", model_type="fairseq")

            # try:
                # self.trans = GoogleTranslator()
                # self.transen = GoogleTranslator(source="en", target="hi")

            # except Exception as args:
            #     print("ERROR TRANS INIT:", args)
            #     self.use_translation = False

    def __call__(self, query, **kwargs):
        return self.rank(query, **kwargs)
    
    def add_docs(self, docs):
        self.docs.extend(docs)

        if self.use_bm25:
            self.BM25model.add_docs(docs)
            
        if self.use_ft:
            self.FTmodel.add_docs(docs)


    def translate(self, text):
        assert self.use_translation, "Translator not initialized"

        print("Hi -> En")
        return self.trans.translate_paragraph(text, "hin_Deva", "eng_Latn")

    @staticmethod
    def mergeranks(idx1, score1, idx2, score2, w1=1, w2=1):
        temp = defaultdict(float)
        for i, s in zip(idx1, score1):
            temp[i] += s * w1

        for i, s in zip(idx2, score2):
            temp[i] += s * w2
        
        idxf = sorted(temp, key=lambda x: temp[x])

        return idxf #, [temp[i] / (w1 + w2) for i in idxf]   



    def RFF(self, ranklists, k, max_out, cutoff, thresh):
        # Reciprocal Rank Fusion
        docrrf = [0] * len(self.docs)
        for num, idx in enumerate(ranklists):
            print("len%d" % num, len(idx), end="\t")
            for rank, i in enumerate(idx):
                docrrf[i] += 1 / (k + rank)

        metric = np.array(docrrf) * k / len(ranklists)
        idx = metric.argsort()[-max_out:][::-1]
        res = metric[idx].round(3)

        idx = idx[(res >= cutoff) & (res >= res[0] * thresh)]
        res = res[(res >= cutoff) & (res >= res[0] * thresh)]

        return idx, res

     
        

    def rank(self, query, thresh=0.4, cutoff=0.2, max_out=20, k=5):
        ts = time()

        assert k >= 1, "Select k >= 1"

        if len(re.sub("\W+", "", query)) < 3:
            return [], []


        results = []
        indices = set()

        transquery = None
        if self.use_translation:
            # if not english
            enchars = re.sub("[^A-Za-z0-9]", "", query)
            # print(enchars)
            if len(enchars) < 0.6 * len(query):
                # print("En -> Hi")
                try:
                    transquery = self.translate(query)
                    print(transquery)
                except Exception as args:
                    print("TRANSLATE ERROR:", args)

        if self.use_bm25:
            bm25idx, bm25res = self.BM25model.rank(query)

            if transquery:
                bm25idx2, bm25res2 = self.BM25model.rank(transquery)
                # bm25idx = self.mergeranks(bm25idx, bm25res, bm25idx2, bm25res2)
                indices |= set(bm25idx2)
                results.append(bm25idx2)

            indices |= set(bm25idx)
            results.append(bm25idx)

        if self.use_ft:
            ftidx, ftres = self.FTmodel.rank(query)

            if transquery:
                ftidx2, ftres2 = self.FTmodel.rank(transquery)
                # ftidx = self.mergeranks(ftidx, ftres, ftidx2, ftres2)
                indices |= set(ftidx2)
                results.append(ftidx2)

            indices |= set(ftidx)
            results.append(ftidx)


        if self.use_bs:
            indices = np.array(list(indices))
            tmpdocs = [self.docs[i] for i in indices]
            print("Total #docs for running bertscore:", len(indices))

            tmpidx, bsres = self.BSmodel.rank(query, tmpdocs)
            if transquery:
                tmpidx2, bsres2 = self.BSmodel.rank(transquery, tmpdocs)
                # tmpidx = self.mergeranks(tmpidx, bsres, tmpidx2, bsres2)
                bsidx2 = indices[tmpidx2]
                results.append(bsidx2)

            bsidx = indices[tmpidx]
            results.append(bsidx)


        if self.use_date_level:
            dateidx = sorted(indices, key=lambda x: self.origdocs[x]['Story_Date'], reverse=True)[:max_out + 1]
            for _ in range(self.use_date_level):
                results.append(dateidx)      


        idx, res = self.RFF(results, k, max_out, cutoff, thresh)


        # sort by date
        # if self.sort_date:
        #     print("SORT DATE NOT IMPLEMENTED")
        #     idx = sorted(idx, key=lambda x: self.origdocs[x]['Story_Date'], reverse = True)
        #     res = metric[idx].round(3)
            

        te = time()
        print("\nQuery time in s:", round(te - ts, 3))
        return idx, res



    def match_percent(self, query, ddict):
        per = self.FTmodel.match_percent(query, ddict)

        # if self.use_translation:
        #     try:
        #         # if not english
        #         enchars = re.sub("[^A-Za-z0-9]", "", query)
        #         # print(enchars)
        #         if len(enchars) < 0.6 * len(query):
        #             # print("En -> Hi")

        #             qt = self.translate(query)
        #             tmp = self.FTmodel.match_percent(qt, ddict)
        #             per = max(per, tmp)
        #     except Exception as args:
        #         print("TRANSLATE ERROR:", args)

        return round(per, 3)

        # return self.BSmodel.match_percent(query, ddict)










################################################################################
################################################################################
if __name__ == "__main__":
    ########################################
    # #### Minimal Example:
    # docs, h = load_data()
    # model = ensemble(docs)

    # idx, res = model(query)

    ########################################
    # QUERY = 'anushka sharma married kohli'
    # QUERY = ['rahul gandhi drinking', 'anushka sharma', 'priyanka chopra', 'priyanka gandhi', 'priyankaa chopra', 'priyankaa gandhi', 'priyankaa gandhi posted', 'virat koli']
    # QUERY = ['virat kohli', 'rahul gandhi drinking', 'beef mcdonald', 'Akhilesh Yadav', 'आलू से सोना', 'Sri lanka economy', 'Rolls Royce Saudi Arabia.', 'Ramu Elephant', 'ms dhoni', 'काल्‍पनिक तस्‍वीर']
    QUERY = ["राहुल गांधी", "नरेंद्र मोदी", "राहुल गांधी बेरोजगार", "Narendra Modi", "Election Fact Check", "Karnataka Election", 'Tejas express', 'Cow Attack Faridabad', 'virat kohli', 'rahul gandhi', 'rahul gandhi drinking', 'beef mcdonald', 'Akhilesh Yadav', 'आलू से सोना', 'Rolls Royce Saudi Arabia.', 'ms dhoni', 'रक्षाबंधन बंपर धमाका को लेकर केबीसी कंपनी के नाम से वायरल किया जा रहा फर्जी पोस्ट', 'केदारनाथ नहीं, 2 साल पहले पाकिस्तान के स्वात घाटी में आई बाढ़ का है वायरल वीडियो']
    # QUERY = ['राहुल गांधी बेरोजगार']
    # QUERY = ["राहुल गांधी", "नरेंद्र मोदी", "Narendra Modi", "Election Fact Check", "Karnataka Election", 'virat kohli', 'rahul gandhi', 'rahul gandhi drinking', 'Akhilesh Yadav', 'ms dhoni']
    # QUERY = ['अंबानी की नई बहू ने अपनी शादी में किया  शास्त्रीय नृत्य', 'आज अखिलेश यादव जी की रथ यात्रा मध्य प्रदेश के निवाडी मे', 'सलमान खान ने पार्कों की साफ़ सफाई के जागरुकता के लिए पार्क में झाड़ू लगाया।', 'केरल बेस्ड मालाबार गोल्ड कंपनी की 99.9% ज्वेलरी हिंदू खरीदते हैं, लेकिन यह कंपनी इस फोटो के अनुसार अपना स्कॉलरशिप 100% सिर्फ मुस्लिम बच्चों को देती है।', 'गोकर्ण (कर्नाटक) के पास एक फ्रांसीसी पर्यटक द्वारा खींची गई एक तस्वीर', 'कंगना ने मानी हार']
    # 7689
    # with open("queries_test.txt") as fp:
    #     QUERY = fp.read().splitlines()

   
    docs, orig = load_data("../csvProcessing/allData.json")
    model = ensemble(docs, use_translation=True, origdocs=orig, use_date_level=2)


    # trans = Model("IndicTrans2/en-indic", model_type="fairseq")
    # transquery = trans.batch_translate(QUERY, "eng_Latn", "hin_Deva") 

    # QUERY = [x + " | " + y for x, y in zip(QUERY, transquery)]

    for query in QUERY:
        
        # print("\n\n")
        # print("#"*100)
        # print("#"*100)
        # print("#"*40 + " BM25 " + "#"*40)
        # print("QUERY:", query)

        
        # indices = set()
        
        # idx, res = model.BM25model.rank(query)
        # indices |= set(idx)
        # for i, v in zip(idx[:10], res[:10]): 
        #     print(" --> ", v, i, docs[i])


        # print("\n")
        # print("#"*40 + " FT-sent " + "#"*40)
        # print("QUERY:", query)
        
        # idx, res = model.FTmodel(query)
        # indices |= set(idx)
        # for i, v in zip(idx[:10], res[:10]): 
        #     print(" --> ", v, i, docs[i])


        # print("\n")
        # print("#"*40 + " BERTSCORE " + "#"*40)
        # print("QUERY:", query)

        # indices = np.array(list(indices))
        # print(len(indices))
        # tmpdocs = [model.docs[i] for i in indices]    
        # idx, res = model.BSmodel(query, tmpdocs)
        # idx = indices[idx]
        # for i, v in zip(idx[:10], res[:10]): 
        #     print(" --> ", v, i, docs[i])
        
        
        

        # Main running method
        print("\n")
        print("#"*40 + " Ensemble " + "#"*40)
        print("QUERY:", query)
        

        idx, scores = model.rank(query)
        percent = (
                max(scores[0], model.match_percent(query, orig[idx[0]]))
                if len(idx) > 0
                else None
            )
        print("Num res:", len(idx))
        print("Percent Match", percent)

        for i, v in zip(idx[:], scores[:]):
            print(" --> ", v, i, docs[i])
            print(" +-> ", orig[i]["Story_Date"], orig[i]["Headline"])
            print()



