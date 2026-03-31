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

    return clean, filepath

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

# -------------------------
# RUN (COMPATIBLE CON RENDER)
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)