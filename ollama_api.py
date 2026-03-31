from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

@app.route("/generate", methods=["POST"])
def generate():
    prompt = request.json.get("prompt")

    response = requests.post(OLLAMA_URL, json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })

    result = response.json()

    return jsonify({
        "text": result.get("response", "")
    })

if __name__ == "__main__":
    app.run(port=5001)