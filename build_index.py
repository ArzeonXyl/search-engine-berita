# build_index.py

import json
import string
import pickle
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

def preprocess_text(text, stemmer, stop_words):
    """
    Fungsi untuk membersihkan, tokenize, menghapus stopwords, dan stemming teks.
    """
    # 1. Hapus tanda baca dan angka
    text = text.translate(str.maketrans('', '', string.punctuation + string.digits))
    # 2. Ubah ke huruf kecil dan pisahkan menjadi kata
    tokens = text.lower().split()
    
    processed_tokens = {}
    for token in tokens:
        # 3. Lakukan stemming
        stemmed_token = stemmer.stem(token)
        # 4. Hapus stopwords dan kata-kata pendek
        if len(stemmed_token) > 2 and stemmed_token not in stop_words:
            # Hitung frekuensi kemunculan term
            processed_tokens[stemmed_token] = processed_tokens.get(stemmed_token, 0) + 1
            
    return processed_tokens

def create_index(json_file_path, stopwords_file_path):
    """
    Membaca dataset JSON, melakukan preprocessing, dan membuat file indeks.
    """
    print("Memulai proses indexing...")

    # Load dataset JSON
    print(f"Membaca dataset dari: {json_file_path}")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        original_docs = json.load(f)

    # Load stopwords
    print(f"Membaca stopwords dari: {stopwords_file_path}")
    with open(stopwords_file_path, 'r', encoding='utf-8') as f:
        stop_words = set(f.read().splitlines()) # Menggunakan set untuk pencarian lebih cepat

    # Inisialisasi Stemmer Sastrawi
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    bow_collection = [] # Bag-of-Words untuk setiap dokumen
    doc_lengths = []    # Panjang setiap dokumen (jumlah kata)
    df = {}             # Document Frequency untuk setiap term

    print("Memproses setiap dokumen (preprocessing, stemming, dll)...")
    for i, doc in enumerate(original_docs):
        # Gabungkan judul dan isi berita untuk diindeks
        content_to_process = doc['judul'] + " " + doc['isi_berita']
        
        # Lakukan preprocessing
        processed_terms = preprocess_text(content_to_process, stemmer, stop_words)
        
        # Simpan hasil
        bow_collection.append(processed_terms)
        doc_lengths.append(sum(processed_terms.values()))

        # Update Document Frequency (DF)
        for term in processed_terms:
            df[term] = df.get(term, 0) + 1

        if (i + 1) % 100 == 0:
            print(f"  ... {i + 1} / {len(original_docs)} dokumen diproses.")

    print("Preprocessing dan perhitungan DF selesai.")

    # Gabungkan semua data yang dibutuhkan untuk search ke dalam satu dictionary
    index_data = {
        "bow_collection": bow_collection,
        "doc_lengths": doc_lengths,
        "document_frequency": df,
        "original_docs": original_docs # Simpan juga data asli untuk ditampilkan di hasil
    }

    # Simpan index menggunakan pickle untuk efisiensi
    output_path = 'bm25_index.pkl'
    print(f"Menyimpan index ke file: {output_path}")
    with open(output_path, 'wb') as f_out:
        pickle.dump(index_data, f_out)

    print(f"\n✅ Indexing selesai! File '{output_path}' telah dibuat.")
    print(f"Total dokumen diindeks: {len(original_docs)}")
    print(f"Total term unik ditemukan: {len(df)}")


if __name__ == "__main__":
    # --- PENGATURAN ---
    # Ganti dengan path ke file dataset JSON Anda
    DATASET_PATH = 'hasil_scraper_tribunnews_multitag/tribun_sports_1393_artikel_2025-06-17_06-35-41.json'
    # Pastikan file stopwords.txt ada di direktori yang sama
    STOPWORDS_PATH = 'stopwords.txt'

    # --- EKSEKUSI ---
    create_index(DATASET_PATH, STOPWORDS_PATH)