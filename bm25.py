# bm25.py

import math
import string
# Library Sastrawi akan diinisialisasi di search_logic.py

def preprocess_query(text, stemmer, stop_words):
    """
    Fungsi untuk membersihkan, tokenize, menghapus stopwords,
    dan stemming query teks dari pengguna.
    """
    text = text.translate(str.maketrans('', '', string.punctuation + string.digits))
    tokens = text.lower().split()
    
    processed_tokens = {}
    for token in tokens:
        stemmed_token = stemmer.stem(token)
        if len(stemmed_token) > 2 and stemmed_token not in stop_words:
            processed_tokens[stemmed_token] = processed_tokens.get(stemmed_token, 0) + 1
            
    return processed_tokens

def score_BM25(N, avdl, doc_lengths, bow_collection, query_terms, df):
    """
    Menghitung skor BM25 untuk semua dokumen berdasarkan query.
    Semua data (N, avdl, dll) didapatkan dari file index yang sudah dimuat.
    """
    k1 = 1.2
    b = 0.75
    query_result = {}

    for doc_id, doc_bow in enumerate(bow_collection):
        score = 0.0
        doc_len = doc_lengths[doc_id]
        
        for term, qtf in query_terms.items():
            if term in df:
                n = df[term]  # Document frequency of the term
                f = doc_bow.get(term, 0) # Term frequency in the current document
                
                # Formula IDF (Inverse Document Frequency)
                idf = math.log10(1 + (N - n + 0.5) / (n + 0.5))
                
                # Formula utama BM25
                numerator = f * (k1 + 1)
                denominator = f + k1 * (1 - b + b * (doc_len / avdl))
                
                score += idf * (numerator / denominator)
        
        query_result[doc_id] = score
        
    return query_result
