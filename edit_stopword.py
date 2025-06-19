# Membuka file dan membaca barisnya
with open("stopwords.txt", "r", encoding="utf-8") as file:
    words = file.readlines()

# Mengedit setiap kata agar memiliki titik setelahnya
edited_words = [word.strip() + "," for word in words]

# Menyimpan hasil kembali ke file
with open("stopwords_indonesia.txt", "w", encoding="utf-8") as file:
    file.write("\n".join(edited_words))

print("File berhasil diedit!")
