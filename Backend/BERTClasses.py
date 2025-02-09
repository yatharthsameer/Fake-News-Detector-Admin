import os

# Disable CUDA
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from bert_score import BERTScorer
from rank_bm25 import BM25Plus
import fasttext
from sklearn.metrics.pairwise import cosine_similarity

# from deep_translator import GoogleTranslator
import json
from time import time
import re
import string
from collections import defaultdict
import spacy
import numpy as np

# from multiprocessing import Pool, Process
from datetime import datetime

from IndicTrans2.inference.engine import Model as IT2Model


def load_data(filepath="csvProcessing/allData.json"):
    docs = []
    with open(filepath) as fp:
        data = json.load(fp)
        origdata = []
        for key in sorted(data, key=int):
            val = data[key]
            val["key"] = key

            try:
                val["Story_Date"] = datetime.strptime(
                    re.sub("(st|nd|rd|th)\s+", " ", val["Story_Date"]), "%d %b %Y"
                )
            except ValueError as args:
                print("Time error:", args)
                continue

            origdata.append(val.copy())
            del val["Story_Date"]
            del val["key"]

            val["Story_URL"] = re.sub(
                "\W+", " ", val["Story_URL"][val["Story_URL"].rfind("/", 0, -2) + 1 :]
            ).strip()

            for x in val:
                # Check if the value is a list
                if isinstance(val[x], list):
                    # Process each item in the list
                    val[x] = [
                        (
                            re.sub("\s+", " ", item.lower()).strip()
                            if item and item.lower() not in ["na", "n/a"]
                            else ""
                        )
                        for item in val[x]
                    ]
                else:
                    val[x] = (
                        re.sub("\s+", " ", val[x].lower()).strip()
                        if val[x] and val[x].lower() not in ["na", "n/a"]
                        else ""
                    )
                    val[x] = (
                        re.sub("(quick.)?fact.check\s?\:?\s*", "", val[x])
                        if val[x].startswith("fact check")
                        or val[x].startswith("fact-check")
                        or val[x].startswith("quick fact check")
                        else val[x]
                    )

            tmp = [
                f'"{val[x].strip(": ")}"'
                for x in [
                    "Story_URL",
                    "Headline",
                    "What_(Claim)",
                    "About_Subject",
                    "About_Person",
                    "tags",
                ]
            ]
            docs.append(" | ".join(tmp))

    return docs, origdata


def quote_match(quote, docset):
    # print(quote, doc)
    for word in quote.split():
        if word not in docset:
            return False
    return True


def doc_tokenize_sets(doc):
    stmp = set(doc.split())
    return stmp


################################################################################
################################################################################
class bm25:
    def __init__(self, docs, orig_docs=None, use_lemma=True):
        self.use_lemma = use_lemma
        ts = time()
        self.nlp = spacy.load("en_core_web_sm")
        self.docs = [self.clean(x) for x in docs]
        self.orig_docs = orig_docs
        self.docs_set = [doc_tokenize_sets(x) for x in self.docs]

        if orig_docs is not None:
            self.title_set = [
                doc_tokenize_sets(self.clean(x["Headline"])) for x in self.orig_docs
            ]

        assert (
            not use_lemma or orig_docs
        ), "Require original docs for doc ID checking during lemma"
        assert len(docs) == len(orig_docs)

        tokenized_corpus = self.tokenize_all(docs, orig_docs)

        self.scorer = BM25Plus(tokenized_corpus)
        te = time()

        print("BM25 Loading time in s:", round(te - ts, 3))

    def __call__(self, query, **kwargs):
        return self.rank(query, **kwargs)

    def add_docs(self, docs, orig_docs=None):
        newdocs = [self.clean(x) for x in docs]
        self.docs.extend(newdocs)
        self.docs_set.extend([doc_tokenize_sets(x) for x in newdocs])

        if self.orig_docs:
            assert orig_docs
            self.orig_docs.extend(orig_docs)
            self.title_set.extend(
                [doc_tokenize_sets(self.clean(x["Headline"])) for x in orig_docs]
            )

        tokenized_corpus = self.tokenize_all(self.docs, self.orig_docs)

        self.scorer = BM25Plus(tokenized_corpus)

    def clean(self, text: str):
        return text.lower()

    def tokenize_all(self, docs, orig_docs):
        if self.use_lemma:
            if not os.path.exists("csvProcessing/"):
                os.makedirs("csvProcessing/")
            try:
                with open("csvProcessing/lemmaData.json") as fr:
                    lemma_data = json.load(fr)

            except Exception as args:
                print("ERROR LOADING LEMMA TEXTS, RECOMPUTING!", args)
                lemma_data = {}

            # compute additional documents
            tokenized_corpus = []
            updateFile = False
            for d, od in zip(docs, orig_docs):
                if od["key"] in lemma_data:
                    tokenized_corpus.append(lemma_data[od["key"]])
                else:
                    tokenized_corpus.append(self.tokenize(d))
                    updateFile = True

            if updateFile:
                print("UPDATING LEMMA FILE")
                with open("csvProcessing/lemmaData.json", "w") as fw:
                    json.dump(
                        {od["key"]: le for le, od in zip(tokenized_corpus, orig_docs)},
                        fw,
                        indent=4,
                        ensure_ascii=False,
                    )

        else:
            tokenized_corpus = map(self.tokenize, docs)

        return tokenized_corpus

    def tokenize(self, text: str):
        if self.use_lemma:
            return [x.lemma_.lower() for x in self.nlp(text)]
        return text.split()

    def rank(self, query: str, thresh=0.6, max_out=25, quoted=None, intitle=None):
        ts = time()

        tokenized_query = self.tokenize(self.clean(query))
        scores = self.scorer.get_scores(tokenized_query)
        metric = scores.round(decimals=2)

        idx = metric.argsort()[::-1]

        if quoted:
            idx = np.array([i for i in idx if quote_match(quoted, self.docs_set[i])])
            if len(idx) == 0:
                return [], []

        if intitle:
            idx = np.array([i for i in idx if quote_match(intitle, self.title_set[i])])
            if len(idx) == 0:
                return [], []

        res = metric[idx]

        # print(idx)
        idx = idx[res >= res[0] * thresh]
        res = res[res >= res[0] * thresh]
        te = time()

        return idx[:max_out], res[:max_out]


################################################################################
################################################################################
class ftsent:
    def __init__(self, docs, orig_docs=None, model_path="fasttext-tmp/model.bin"):
        ts = time()
        self.model = fasttext.load_model(model_path)
        self.doc_vecs = [self.model.get_sentence_vector(x) for x in docs]
        self.docs_set = [doc_tokenize_sets(self.clean(x)) for x in docs]
        self.orig_docs = orig_docs


        if orig_docs is not None:
            self.title_set = [
                doc_tokenize_sets(self.clean(x["Headline"])) for x in orig_docs
            ]
        te = time()

        print("FT-sent Loading time in s:", round(te - ts, 3))

    def clean(self, text: str):
        return text.lower()

    def __call__(self, query, **kwargs):
        return self.rank(query, **kwargs)

    def add_docs(self, docs, orig_docs=None):
        self.doc_vecs.extend([self.model.get_sentence_vector(x) for x in docs])
        self.docs_set.extend([doc_tokenize_sets(self.clean(x)) for x in docs])

        if self.orig_docs:
            assert orig_docs
            self.title_set.extend(
                [doc_tokenize_sets(self.clean(x["Headline"])) for x in orig_docs]
            )

    def rank(
        self, query: str, thresh=0.85, cutoff=0.6, max_out=25, quoted=None, intitle=None
    ):
        ts = time()
        query_vec = self.model.get_sentence_vector(self.clean(query))
        cos_sim = cosine_similarity([query_vec], self.doc_vecs)

        metric = (cos_sim[0] * 100).round(decimals=2)

        idx = metric.argsort()[::-1]

        if quoted:
            idx = np.array([i for i in idx if quote_match(quoted, self.docs_set[i])])
            if len(idx) == 0:
                return [], []

        if intitle:
            idx = np.array([i for i in idx if quote_match(intitle, self.title_set[i])])
            if len(idx) == 0:
                return [], []

        res = metric[idx]

        idx = idx[(res >= cutoff) & (res >= res[0] * thresh)]
        res = res[(res >= cutoff) & (res >= res[0] * thresh)]

        te = time()

        return idx[:max_out], res[:max_out]

    def match_percent(self, query, ddict):
        query_vec = self.model.get_sentence_vector(self.clean(query))
        doc_vec = self.model.get_sentence_vector(self.clean(ddict["Headline"]))
        return cosine_similarity([query_vec], [doc_vec])[0][0]


################################################################################
################################################################################
class bertscore:
    def __init__(self, docs=[], orig_docs=None):
        ts = time()
        self.scorer = BERTScorer(model_type="distilbert-base-multilingual-cased")
        self.docs = [self.clean(x) for x in docs]
        self.docs_set = [doc_tokenize_sets(x) for x in self.docs]

        if orig_docs:
            self.title_set = [
                doc_tokenize_sets(self.clean(x["Headline"])) for x in orig_docs
            ]

        te = time()

        print("BertScore Loading time in s:", round(te - ts, 3))

    def clean(self, text: str):
        return text.lower()

    def __call__(self, query, docs=None, **kwargs):
        return self.rank(query, docs, **kwargs)

    def add_docs(self, docs, orig_docs=None):
        newdocs = [self.clean(x) for x in docs]
        self.docs.extend(newdocs)
        self.docs_set.extend([doc_tokenize_sets(x) for x in newdocs])

        if self.orig_docs:
            assert orig_docs
            self.title_set.extend(
                [doc_tokenize_sets(self.clean(x["Headline"])) for x in orig_docs]
            )

    def rank(
        self,
        query: str,
        docs=None,
        thresh=0.8,
        cutoff=0.6,
        max_out=25,
        quoted=None,
        intitle=None,
    ):
        ts = time()

        refs = self.docs if docs is None else docs
        cands = [self.clean(query)] * len(refs)

        P, R, F1 = self.scorer.score(cands, refs)
        metric = (F1.numpy() * 100).round(decimals=2)

        idx = metric.argsort()[::-1]

        if quoted and docs is None:
            idx = np.array([i for i in idx if quote_match(quoted, self.docs_set[i])])
            if len(idx) == 0:
                return [], []

        if intitle and docs is None:
            idx = np.array([i for i in idx if quote_match(intitle, self.title_set[i])])
            if len(idx) == 0:
                return [], []

        res = metric[idx]

        idx = idx[(res >= cutoff) & (res >= res[0] * thresh)]
        res = res[(res >= cutoff) & (res >= res[0] * thresh)]
        te = time()

        return idx[:max_out], res[:max_out]

    def match_percent(self, query, ddict):
        return self.scorer.score([query], [ddict["Headline"]])[0]


################################################################################
################################################################################
class ensemble:

    def __init__(
        self,
        docs,
        use_bm25=True,
        use_ft=True,
        use_bs=True,
        use_translation=False,
        use_date_level=1,
        orig_docs=None,
    ):
        self.use_bm25 = use_bm25
        self.use_ft = use_ft
        self.use_bs = use_bs
        self.use_translation = use_translation
        self.use_date_level = use_date_level
        self.orig_docs = orig_docs
        self.docs = docs

        assert use_bm25 or use_ft or use_bs, "Select at least 1 model"

        assert not use_date_level or orig_docs, "Need original docs if using date"

        if use_bm25:
            self.BM25model = bm25(docs, orig_docs)

        if use_ft:
            self.FTmodel = ftsent(docs, orig_docs)

        if use_bs:
            self.BSmodel = bertscore()

        if use_translation:
            self.trans = IT2Model(
                "IndicTrans2/ct2_fp16_model", model_type="ctranslate2", device="cpu"
            )

    def __call__(self, query, **kwargs):
        return self.rank(query, **kwargs)

    def preprocess_query(self, query):
        tmp = re.sub(
            "[%s]" % re.escape(string.punctuation.replace("'", "")), " ", query
        ).strip()
        tmp = tmp.replace("'", "")
        # tmp = re.sub(r"[^\w\s]+", " ", query, re.UNICODE).strip()
        tmp = [x for x in tmp.split() if len(x) > 1]
        tmp = " ".join(tmp)
        return tmp

    def find_quote(self, query):
        # print(query)
        tmp = " ".join(re.findall('".+?"', query))
        tmp = re.sub(
            "[%s]" % re.escape(string.punctuation.replace("'", "")), " ", tmp
        ).strip()
        tmp = tmp.replace("'", "")
        # tmp = re.sub(r"[^\w\s]+", " ", tmp, re.UNICODE).strip()
        return tmp.lower()

    def find_intitle(self, query):
        tmp1 = [
            y
            for x in re.findall("intitle:\S+", query)
            for y in re.sub(
                "[%s]" % re.escape(string.punctuation.replace("'", "")), " ", x[8:]
            )
            .replace("'", "")
            .strip()
            .split()
        ]

        # tmp = re.sub(r"[^\w\s]+", " ", tmp, re.UNICODE).strip()
        tmp2 = [
            y
            for x in re.findall('intitle:".+?"', query)
            for y in re.sub(
                "[%s]" % re.escape(string.punctuation.replace("'", "")), " ", x[9:-1]
            )
            .replace("'", "")
            .strip()
            .split()
        ]
        # print(tmp1)
        # print(tmp2)

        tmp = " ".join(set(tmp1) | set(tmp2))
        return tmp.lower()

    def add_docs(self, docs, orig_docs=None):
        self.docs.extend(docs)

        if self.orig_docs:
            assert orig_docs

        if self.use_bm25:
            self.BM25model.add_docs(docs, orig_docs)

        if self.use_ft:
            self.FTmodel.add_docs(docs, orig_docs)

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

        return idxf

    def RFF(self, ranklists, k, max_out, cutoff, thresh):
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

    ################################################################################
    ################################################################################
    def rank(self, query, thresh=0.4, cutoff=0.2, max_out=20, k=5):
        ts = time()

        assert k >= 1, "Select k >= 1"

        quote = self.find_quote(query)
        intitle = self.find_intitle(query)
        query = self.preprocess_query(query)

        print("QUERY:", query)
        if quote:
            print("QUOTED:", quote)

        if intitle:
            print("INTITLE:", intitle)

        if len(query) < 3:
            print("Too short query")
            return [], []

        results = []
        indices = set()

        transquery = None
        if self.use_translation:
            enchars = re.sub("[^A-Za-z0-9]", "", query)
            if len(enchars) < 0.6 * len(query):
                try:
                    transquery = self.translate(query)
                    print(transquery)
                except Exception as args:
                    print("TRANSLATE ERROR:", args)

        if self.use_bm25:
            bm25idx, bm25res = self.BM25model.rank(query, quoted=quote, intitle=intitle)

            if transquery:
                bm25idx2, bm25res2 = self.BM25model.rank(
                    transquery, quoted=quote, intitle=intitle
                )
                indices |= set(bm25idx2)
                results.append(bm25idx2)

            # NEW CHANGE: CLIPPING INPUT INDICES FOR BS
            indices |= set(bm25idx[:15])
            results.append(bm25idx)

        if self.use_ft:
            ftidx, ftres = self.FTmodel.rank(query, quoted=quote, intitle=intitle)

            if transquery:
                ftidx2, ftres2 = self.FTmodel.rank(
                    transquery, quoted=quote, intitle=intitle
                )
                indices |= set(ftidx2)
                results.append(ftidx2)

            # NEW CHANGE: CLIPPING INPUT INDICES FOR BS
            indices |= set(ftidx[:15])
            results.append(ftidx)

        if not indices:
            print("No matching quoted terms in any doc")
            return [], []

        if self.use_bs:
            indices = np.array(list(indices))
            tmpdocs = [self.docs[i] for i in indices]
            print("Total #docs for running bertscore:", len(indices))

            tmpidx, bsres = self.BSmodel.rank(
                query, tmpdocs, quoted=quote, intitle=intitle
            )
            if transquery:
                tmpidx2, bsres2 = self.BSmodel.rank(
                    transquery, tmpdocs, quoted=quote, intitle=intitle
                )
                bsidx2 = indices[tmpidx2]
                results.append(bsidx2)

            bsidx = indices[tmpidx]
            results.append(bsidx)

        if self.use_date_level:
            dateidx = sorted(
                indices, key=lambda x: self.orig_docs[x]["Story_Date"], reverse=True
            )[: max_out + 1]
            for _ in range(self.use_date_level):
                results.append(dateidx)

        idx, res = self.RFF(results, k, max_out, cutoff, thresh)

        te = time()
        print("\nQuery time in s:", round(te - ts, 3))
        return idx, res

    def match_percent(self, query, ddict):
        per = self.FTmodel.match_percent(query, ddict)
        return round(per, 3)


################################################################################
################################################################################
if __name__ == "__main__":
    # QUERY = ['"Deepinder Goyal"', '"Shivam Dube"', '"Bad Blood"', '"Suryakumar Yadav"', '"Liverpool"', '"Mukesh Ambani"', '"Haryana Election"', '"Bangalore weather"']
    # QUERY = ["राहुल गांधी", "राहुल गांधी बेरोजगार", 'rahul gandhi', 'rahul gandhi drinking', "नरेंद्र मोदी",  "Narendra Modi", "Election Fact Check", "Karnataka Election", 'Tejas express', 'Cow Attack Faridabad', 'virat kohli', 'rahul gandhi', 'rahul gandhi drinking', 'beef mcdonald', 'Akhilesh Yadav', 'आलू से सोना', 'Rolls Royce Saudi Arabia.', 'ms dhoni', 'रक्षाबंधन बंपर धमाका को लेकर केबीसी कंपनी के नाम से वायरल किया जा रहा फर्जी पोस्ट', 'केदारनाथ नहीं, 2 साल पहले पाकिस्तान के स्वात घाटी में आई बाढ़ का है वायरल वीडियो']
    # QUERY = ['rahul gandhi intitle:drinking', 'rahul gandhi intitle:"drinking"']#,  'intitle:"rahul gandhi" drinking', 'intitle:"rahul gandhi drinking"']

    QUERY = (
        []
        + ["Kisan", "Kisan", "Haryana", "England Women", "Scotland Women", "Navratri"]
        + ["Barcelona", "BAN", "Madrid"]
        + ["Chennai", "Ind", "United"]
    )
    # ['Vijay Sethupathi', 'Deepinder Goyal', 'Bad Blood 2024', 'Suryakumar Yadav', 'UFC 307', 'Haryana Election', 'George Soros', 'Sonam Wangchuk', 'NBA', 'The Great Indian Kapil Show', 'Antarctica', 'Mukesh Ambani'] \

    docs, orig = load_data("csvProcessing/allData.json")
    model = ensemble(docs, use_translation=True, orig_docs=orig, use_date_level=1)

    for query in QUERY:
        query = '"' + query + '"'
        print("\n")
        print("#" * 40 + " Ensemble " + "#" * 40)

        idx, scores = model.rank(query)
        percent = (
            max(list(scores[:3]) + [model.match_percent(query, orig[idx[0]])])
            if len(idx) > 0
            else None
        )
        print("Num res:", len(idx))
        print("Percent Match", percent)

        for i, v in zip(idx[:1], scores[:1]):
            print(" --> ", v, i, docs[i])
            print(" +-> ", orig[i]["Headline"])
            print()
