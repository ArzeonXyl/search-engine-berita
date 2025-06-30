# app.py

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS # Menambahkan CORS untuk pengembangan lokal

from search_logic import perform_search 

app = Flask(__name__, template_folder='views')
CORS(app) 

@app.route('/')
def index():
    # Menampilkan halaman utama
    return render_template('index.html')

@app.route("/run-python", methods=["POST"])
def run_python():
    data = request.get_json()
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "Query tidak boleh kosong!"}), 400

    try:
        # Panggil fungsi perform_search secara langsung
        result_json_string = perform_search(query)
        # Respon sudah dalam bentuk JSON string, jadi kita kirim sebagai dictionary
        return jsonify({"output": result_json_string})
    except Exception as e:
        print(f"Error saat search: {e}")
        return jsonify({"error": "Terjadi kesalahan internal pada server", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
