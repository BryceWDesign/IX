from flask import Flask, request, jsonify
from src.parser import parse_and_run

app = Flask(__name__)

@app.route("/run", methods=["POST"])
def run_ix():
    data = request.get_json()
    code = data.get("code", "")
    try:
        result = parse_and_run(code)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
