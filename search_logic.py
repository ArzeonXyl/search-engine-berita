# search_logic.py

import json
import pickle
import os
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
# Mengimpor fungsi dari bm25.py yang sudah diperbarui
from bm25 import preprocess_query, score_BM25 

current_dir = os.path.dirname(__file__)
stopwords_path = os.path.join(current_dir, 'stopwords.txt')
index_file_path = os.path.join(current_dir, 'hasil_scraper_tribun_sports', 'bm25_index.pkl')

print("Menginisialisasi stemmer dan stopwords...")
try:
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        STOP_WORDS = set(f.read().splitlines())
except FileNotFoundError:
    print(f"ERROR: File stopwords tidak ditemukan di '{stopwords_path}'. Harap pastikan file tersebut ada.")
    STOP_WORDS = set()

STEMMER = StemmerFactory().create_stemmer()
print("Inisialisasi selesai.")

# Memuat file index yang sudah dibuat sebelumnya
print(f"Memuat file index dari: {index_file_path}")
try:
    with open(index_file_path, 'rb') as f_in:
        index_data = pickle.load(f_in)
except FileNotFoundError:
    print(f"❌ FATAL ERROR: File index '{index_file_path}' tidak ditemukan!")
    print("Pastikan Anda sudah menjalankan script 'preprocessing.py' di di folder yang benar.")
    exit() # Hentikan aplikasi jika index tidak ada

BOW_COLLECTION = index_data.get("bow_collection", [])
DOC_LENGTHS = index_data.get("doc_lengths", [])
DF = index_data.get("document_frequency", {})
ORIGINAL_DOCS = index_data.get("original_docs", [])
N = len(ORIGINAL_DOCS) # Jumlah total dokumen
AVDL = sum(DOC_LENGTHS) / N if N > 0 else 0 # Rata-rata panjang dokumen

print(f"✅ Index berhasil dimuat. Total Dokumen: {N}, Rata-rata Panjang: {AVDL:.2f}")


def perform_search(query_text):
    """
    Versi revisi: sekarang balikin JSON berisi:
      - results (list)
      - total_found (int)
      - time_taken (float detik)
    """
    import time
    start_time = time.time()

    if not query_text:
        return json.dumps({
            "results": [],
            "total_found": 0,
            "time_taken": 0
        })

    # 1. Preprocess query
    query_terms = preprocess_query(query_text, STEMMER, STOP_WORDS)

    # 2. Hitung skor BM25
    results = score_BM25(N, AVDL, DOC_LENGTHS, BOW_COLLECTION, query_terms, DF)

    # 3. Urutkan hasil (max 10k)
    top_results = sorted(results.items(), key=lambda x: x[1], reverse=True)[:10000]

    output = []
    for doc_id, score in top_results:
        if score > 0:
            doc_data = ORIGINAL_DOCS[doc_id]
            output.append({
                "judul": doc_data.get('judul', 'Judul tidak tersedia'),
                "url": doc_data.get('url', '#'),
                "isi_berita": doc_data.get('isi_berita', ''),
                "score": score
            })

    end_time = time.time()
    time_taken = round(end_time - start_time, 4)

    return json.dumps({
        "results": output,
        "total_found": len(output),
        "time_taken": time_taken
    }, indent=2, ensure_ascii=False)


