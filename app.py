import os
import hashlib
from flask import Flask, render_template, request, jsonify
import pyttsx3

# =========================
# CONFIG
# =========================

USE_OPENAI = False  # 🔁 cambiar a True cuando actives API

app = Flask(__name__)

# Crear carpeta static si no existe
if not os.path.exists("static"):
    os.makedirs("static")

# =========================
# TTS LOCAL (pyttsx3)
# =========================

engine = pyttsx3.init()

def generar_audio_local(texto):
    # hash para evitar duplicados
    text_hash = hashlib.md5(texto.encode()).hexdigest()
    filename = f"audio_{text_hash}.mp3"
    filepath = os.path.join("static", filename)

    if not os.path.exists(filepath):
        engine.save_to_file(texto, filepath)
        engine.runAndWait()

    return filepath

# =========================
# (RESERVADO) OPENAI TTS
# =========================

"""
from openai import OpenAI
client = OpenAI()

def generar_audio_openai(texto):
    text_hash = hashlib.md5(texto.encode()).hexdigest()
    filename = f"audio_{text_hash}.mp3"
    filepath = os.path.join("static", filename)

    if not os.path.exists(filepath):
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=texto
        ) as response:
            response.stream_to_file(filepath)

    return filepath
"""

# =========================
# ROUTER DE AUDIO
# =========================

def generar_audio(texto):
    if USE_OPENAI:
        # return generar_audio_openai(texto)
        pass
    return generar_audio_local(texto)

# =========================
# GENERADOR DE DRILLS (LOCAL)
# =========================

def generate_drills_ai(n=10):
    # versión local simple (puedes mejorarla luego)
    base = [
        "Ich gehe nach Hause",
        "Du lernst Deutsch",
        "Er trinkt Wasser",
        "Wir spielen im Park",
        "Sie arbeitet heute",
        "Ich esse einen Apfel",
        "Du liest ein Buch",
        "Wir fahren nach Berlin",
        "Er schreibt eine Nachricht",
        "Sie hört Musik"
    ]

    drills = []

    for i in range(n):
        frase = base[i % len(base)]
        audio_path = generar_audio(frase)

        drills.append({
            "text": frase,
            "audio": audio_path
        })

    return drills

# =========================
# (RESERVADO) OPENAI DRILLS
# =========================

"""
def generate_drills_openai(n=10):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"Genera {n} frases en alemán nivel A1"
    )

    texto = response.output_text.split("\n")

    drills = []
    for frase in texto:
        if frase.strip():
            audio_path = generar_audio(frase)
            drills.append({
                "text": frase,
                "audio": audio_path
            })

    return drills
"""

# =========================
# ROUTES
# =========================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate_ai", methods=["POST"])
def generate_ai():
    try:
        if USE_OPENAI:
            # drills = generate_drills_openai(10)
            drills = []
        else:
            drills = generate_drills_ai(10)

        return jsonify(drills)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================
# MAIN
# =========================

if __name__ == "__main__":
    app.run(debug=True)