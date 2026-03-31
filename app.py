import os
import sqlite3
import uuid
import re
from flask import Flask, render_template, request, redirect, url_for
from gtts import gTTS
import qrcode

app = Flask(__name__)

# -------------------------
# CONFIG
# -------------------------
DB_PATH = "database.db"
AUDIO_FOLDER = "/tmp/audio"  # 🔥 importante para nube
QR_FOLDER = "static"

os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

# -------------------------
# DB INIT
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        clean_text TEXT NOT NULL,
        audio_path TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------
# CLEAN TEXT
# -------------------------
def clean_text(text):
    return re.sub(r'[^\w\säöüÄÖÜß]', '', text)

# -------------------------
# GENERATE AUDIO
# -------------------------
def generate_audio(text):
    clean = clean_text(text)

    filename = f"audio_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(AUDIO_FOLDER, filename)

    tts = gTTS(clean, lang="de")
    tts.save(filepath)

    return clean, filename

# -------------------------
# GENERATE QR (DINÁMICO)
# -------------------------
def generate_qr(url):
    filename = f"qr_{uuid.uuid4().hex}.png"
    path = os.path.join(QR_FOLDER, filename)

    qr = qrcode.make(url)
    qr.save(path)

    return path

# -------------------------
# SAVE DRILL
# -------------------------
def save_drill(text):
    clean, audio_path = generate_audio(text)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO drills (text, clean_text, audio_path)
    VALUES (?, ?, ?)
    """, (text, clean, audio_path))

    conn.commit()
    conn.close()

import random

# -------------------------
# GENERADOR DE DRILLS
# -------------------------
def generate_drills(n=20):

    sujetos = ["Ich", "Du", "Er", "Wir", "Sie"]
    
    verbos = [
        ("gebe", "gibst", "gibt", "geben", "geben"),
        ("zeige", "zeigst", "zeigt", "zeigen", "zeigen"),
        ("erkläre", "erklärst", "erklärt", "erklären", "erklären"),
        ("bringe", "bringst", "bringt", "bringen", "bringen"),
        ("kaufe", "kaufst", "kauft", "kaufen", "kaufen")
    ]

    dativos = [
        ("🔵meinem Vater", "🔵deinem Vater", "🔵seinem Vater", "🔵unserem Vater", "🔵ihrem Vater"),
        ("🔴meiner Mutter", "🔴deiner Mutter", "🔴seiner Mutter", "🔴unserer Mutter", "🔴ihrer Mutter"),
        ("🟢meinem Kind", "🟢deinem Kind", "🟢seinem Kind", "🟢unserem Kind", "🟢ihrem Kind")
    ]

    acusativos = [
        ("🔵meinen Bruder", "🔵deinen Bruder", "🔵seinen Bruder", "🔵unseren Bruder", "🔵ihren Bruder"),
        ("🔴meine Tasche", "🔴deine Tasche", "🔴seine Tasche", "🔴unsere Tasche", "🔴ihre Tasche"),
        ("🟢mein Buch", "🟢dein Buch", "🟢sein Buch", "🟢unser Buch", "🟢ihr Buch")
    ]

    drills = []

    for _ in range(n):
        i = random.randint(0, 4)

        sujeto = sujetos[i]
        verbo = random.choice(verbos)[i]
        dativo = random.choice(dativos)[i]
        acusativo = random.choice(acusativos)[i]

        frase = f"{sujeto} {verbo} 🟣{dativo} 🟡{acusativo}"
        drills.append(frase)

    return drills

# -------------------------
# ROUTES
# -------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form.get("content")

        lines = [line.strip() for line in content.split("\n") if line.strip()]

        for line in lines:
            save_drill(line)

        return redirect(url_for("index"))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, audio_path FROM drills ORDER BY id DESC")
    drills = cursor.fetchall()
    conn.close()

    return render_template("index.html", drills=drills)

# -------------------------
# PRINT VIEW (CON QR DINÁMICO)
# -------------------------
@app.route("/print")
def print_view():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM drills ORDER BY id DESC")
    drills = cursor.fetchall()
    conn.close()

    # 🔥 URL dinámica (local o nube)
    base_url = request.host_url

    # aquí usamos la raíz (puedes cambiar luego a sets)
    full_url = base_url

    qr_path = generate_qr(full_url)

    return render_template(
        "print.html",
        drills=drills,
        qr_url=qr_path
    )

from flask import send_file

@app.route("/audio/<filename>")
def serve_audio(filename):
    path = os.path.join(AUDIO_FOLDER, filename)
    return send_file(path)

@app.route("/generate")
def generate():
    drills = generate_drills(20)

    for d in drills:
        save_drill(d)

    return redirect(url_for("index"))


# -------------------------
# RUN (COMPATIBLE CON RENDER)
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)