from flask import Flask, request, jsonify, render_template
import subprocess
import sys
import os

# Kasih tahu Flask template folder-nya "views"
app = Flask(__name__, template_folder='views')

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/run-python", methods=["POST"])
def run_python():
    data = request.get_json()
    query = data.get("query", "")

    script_path = os.path.join(os.getcwd(), "query.py")
    if not os.path.exists(script_path):
        return jsonify({"error": f"Script query.py tidak ditemukan di {script_path}"}), 404

    try:
        result = subprocess.run(
            [sys.executable, script_path, query],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode == 0:
            return jsonify({"output": result.stdout.strip()})
        else:
            return jsonify({
                "error": "Gagal menjalankan query.py",
                "details": result.stderr.strip()
            }), 500

    except Exception as e:
        return jsonify({"error": "Internal error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
