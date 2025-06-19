import json
import string
import math
import sys

sys.path.append('stemming/')
from stemming.porter3 import stem

class BowColl:
    BowCollList = []

class BowDoc:
    def __init__(self, docID, term, docLen):
        self.docID = docID
        self.term = term
        self.docLen = docLen

def preprocess_text(text, stop_words):
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.translate(str.maketrans('', '', string.digits))
    text = text.lower().split()
    processed_text = {}
    for term in text:
        term = stem(term)
        if len(term) > 2 and term not in stop_words:
            processed_text[term] = processed_text.get(term, 0) + 1
    return processed_text

def parse_json_coll(json_file, stop_words):
    original_docs = []
    BowColl.BowCollList = []  # reset biar gak dobel kalau dipanggil ulang
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    for index, item in enumerate(data):
        docID = index
        term = preprocess_text(item["description"], stop_words)
        docLen = sum(term.values())
        BowColl.BowCollList.append([docID, term, docLen])
        original_docs.append(item)
    return BowColl.BowCollList, original_docs

def compute_K(dl, avdl):
    return 1.2 * ((1 - 0.75) + 0.75 * (float(dl) / float(avdl)))

def score_BM25(coll, query, df, stop_words):
    query_terms = preprocess_text(query, stop_words)
    avdl = sum(doc[2] for doc in coll) / len(coll)
    query_result = {}
    k1, k2, b, R, N, r = 1.2, 100, 0.75, 0.0, len(coll), 0.0

    for doc in coll:
        score = 0
        for term in query_terms:
            n = df.get(term, 0)
            f = doc[1].get(term, 0)
            K = compute_K(doc[2], avdl)
            if n == 0:
                continue
            first = math.log10(((r + 0.5) / (R - r + 0.5)) / ((n - r + 0.5) / (N - n - R + r + 0.5)))
            second = ((k1 + 1) * f) / (K + f)
            third = ((k2 + 1) * query_terms[term]) / (k2 + query_terms[term])
            score += first * second * third
        query_result[doc[0]] = score
    return query_result
