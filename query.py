import sys
import io
import json
from bm25 import parse_json_coll, score_BM25

# Supaya output ke terminal pakai encoding UTF-8, biar gak error di Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

if len(sys.argv) < 2:
    print("Usage: python query.py [query]")
    sys.exit(1)

query = " ".join(sys.argv[1:])  # biar bisa input >1 kata juga

# Load stopwords
with open('stopwords_indonesia.txt', 'r') as stopwords_f:
    stop_words = stopwords_f.read().split(',')

# Load data & build BOW
BowDocColl, OriginalDocs = parse_json_coll('data/pahlawan.json', stop_words)

# Hitung DF
df = {}
for doc in BowDocColl:
    for term in doc[1]:
        df[term] = df.get(term, 0) + 1

# Skoring BM25
results = score_BM25(BowDocColl, query, df, stop_words)

# Ambil top 5 hasil
top_results = sorted(results.items(), key=lambda x: x[1], reverse=True)[:10]

# Tampilkan hasil dengan data asli + score
output = []
for doc_id, score in top_results:
    doc = OriginalDocs[doc_id].copy()
    doc["score"] = score
    output.append(doc)

print(json.dumps(output, indent=2, ensure_ascii=False))
