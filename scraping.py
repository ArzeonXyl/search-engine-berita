import requests
import time
import csv
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup

def simpan_ke_csv_tribun(data_berita, nama_folder="hasil_scraper_tribunnews_multitag"):
    if not data_berita:
        print("Tidak ada data untuk disimpan.")
        return

    os.makedirs(nama_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nama_file = f"tribun_sports_{len(data_berita)}_artikel_{timestamp}.csv"
    path_file = os.path.join(nama_folder, nama_file)

    print(f"\nMenyimpan data ke file CSV...")
    fieldnames = ['judul', 'url', 'isi_berita']

    try:
        with open(path_file, 'w', newline='', encoding='utf-8') as file_csv:
            writer = csv.DictWriter(file_csv, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_berita)

        print(f"✅ Data berhasil disimpan di folder '{nama_folder}'")
        print(f"Lokasi file: {os.path.abspath(path_file)}")
    except IOError as e:
        print(f"Gagal menyimpan file. Error: {e}")

def scrape_tribun_by_tags(daftar_tags, link_per_tag=200, batas_kesabaran=3):
    """
    Fungsi utama untuk scraping dari berbagai tag di Tribunnews.
    Akan mencoba mengambil 'link_per_tag' artikel dari setiap tag
    dan memiliki 'batas_kesabaran' untuk pindah tag jika tidak produktif.
    """
    base_url = "https://www.tribunnews.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # --- TAHAP 1: Mengumpulkan Link Artikel ---
    links_artikel_final = []
    print(f"Memulai proses pengumpulan link dengan target {link_per_tag} link per tag...")

    for tag_saat_ini in daftar_tags:
        print(f"\n--- Memproses Tag: '{tag_saat_ini}' ---")
        links_untuk_tag_ini = []
        halaman_saat_ini = 1
        halaman_kosong_berturut_turut = 0 # <-- MEKANISME KESABARAN DIMULAI DARI 0

        while len(links_untuk_tag_ini) < link_per_tag:
            url_halaman_tag = f"{base_url}/tag/{tag_saat_ini}?page={halaman_saat_ini}"
            print(f"   Mencari di halaman {halaman_saat_ini}...")

            try:
                response_daftar = requests.get(url_halaman_tag, headers=headers, timeout=15)
                if response_daftar.status_code != 200:
                    print(f"   Halaman tidak ditemukan, tag '{tag_saat_ini}' selesai.")
                    break

                soup_daftar = BeautifulSoup(response_daftar.text, 'html.parser')
                elemen_ditemukan = soup_daftar.select('li.ptb15 h3 a')

                if not elemen_ditemukan:
                    print(f"   Tidak ada artikel lagi di tag '{tag_saat_ini}'. Tag selesai.")
                    break

                link_baru_di_halaman_ini = 0
                for item in elemen_ditemukan:
                    url_artikel = item.get('href')
                    if url_artikel and url_artikel not in links_artikel_final:
                        links_untuk_tag_ini.append(url_artikel)
                        links_artikel_final.append(url_artikel)
                        link_baru_di_halaman_ini += 1
                        if len(links_untuk_tag_ini) >= link_per_tag:
                            break

                print(f"   -> Ditemukan {link_baru_di_halaman_ini} link baru. Total untuk tag ini: {len(links_untuk_tag_ini)}.")

                # --- Logika Mekanisme Kesabaran ---
                if link_baru_di_halaman_ini == 0:
                    halaman_kosong_berturut_turut += 1
                    print(f"   -> Halaman kosong ke-{halaman_kosong_berturut_turut}. Batas kesabaran: {batas_kesabaran}.")
                else:
                    halaman_kosong_berturut_turut = 0 # Reset kesabaran jika menemukan link baru

                if halaman_kosong_berturut_turut >= batas_kesabaran:
                    print(f"   -> Telah mencapai batas kesabaran. Pindah ke tag berikutnya.")
                    break
                # --- Akhir Logika Kesabaran ---

                halaman_saat_ini += 1
                time.sleep(0.5)

            except requests.exceptions.RequestException as e:
                print(f"Gagal mengakses halaman. Error: {e}")
                break

        print(f"-> Selesai untuk tag '{tag_saat_ini}', total terkumpul {len(links_untuk_tag_ini)} link unik dari tag ini.")

    print(f"\n✅ Pengumpulan link selesai. Total link unik dari semua tag: {len(links_artikel_final)}\n")
    if not links_artikel_final:
        return

    # --- TAHAP 2 & 3: Scraping Artikel dan Menyimpan ke CSV ---
    # (Bagian ini tidak perlu diubah, karena sudah berfungsi dengan baik)
    semua_data_berita = []
    for i, link in enumerate(links_artikel_final):
        print(f"--- Scraping Artikel #{i+1} dari {len(links_artikel_final)} ---")
        try:
            response_artikel = requests.get(link, headers=headers, timeout=15)
            response_artikel.raise_for_status()
            soup_artikel = BeautifulSoup(response_artikel.text, 'html.parser')

            judul_element = soup_artikel.select_one('h1#arttitle')
            judul = judul_element.get_text(strip=True) if judul_element else "Judul tidak ditemukan"

            konten_element = soup_artikel.select_one('div.side-article.txt-article')
            if konten_element:
                for elemen_tidak_penting in konten_element.select('.baca, .ads-placeholder, figure, script, style, .tagcloud3, .mb10.f16.ln24'):
                    elemen_tidak_penting.decompose()
                isi_berita = konten_element.get_text(separator='\n', strip=True)
            else:
                isi_berita = "Isi berita tidak ditemukan."

            semua_data_berita.append({'judul': judul, 'url': link, 'isi_berita': isi_berita})
            time.sleep(1)
        except requests.exceptions.RequestException as e:
            print(f"Gagal mengambil artikel di {link}. Error: {e}")

    simpan_ke_csv_tribun(semua_data_berita)

if __name__ == "__main__":
    # --- PANEL KONTROL ---
    TAGS_OLAHRAGA = [
        'tenis', 'motogp', 'bulutangkis', 'formula-1',
        'liga-indonesia', 'liga-inggris', 'sea-games-2023'
    ]
    LINK_PER_TAG = 200
    # Atur seberapa "sabar" scraper harus mencoba halaman kosong sebelum pindah tag.
    BATAS_KESABARAN_HALAMAN = 3

    NAMA_FOLDER_OUTPUT = "hasil_scraper_tribun_sports"

    # --- EKSEKUSI SCRAPER ---
    scrape_tribun_by_tags(
        daftar_tags=TAGS_OLAHRAGA,
        link_per_tag=LINK_PER_TAG,
        batas_kesabaran=BATAS_KESABARAN_HALAMAN
    )