import subprocess # Para ejecutar Piper si no usas la librería directa
import os
import sqlite3
import uuid
import re
from flask import Flask, render_template, request, redirect, url_for
from gtts import gTTS
import qrcode
import asyncio
import edge_tts
from gtts import gTTS

import ollama

app = Flask(__name__)

# -------------------------
# CONFIG
# -------------------------
DB_PATH = "database.db"
AUDIO_FOLDER = "/tmp/audio"  # 🔥 importante para nube
QR_FOLDER = "static"

os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

# CONFIGURACIÓN DE AUDIO
USE_LOCAL_TTS = True  # <--- Cambia a False para volver a gTTS
PIPER_MODEL = "models/de_DE-thorsten-medium.onnx"


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

def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

# -------------------------
# CLEAN TEXT
# -------------------------
def clean_text(text):
    return re.sub(r'[^\w\säöüÄÖÜß]', '', text)

# -------------------------
# GENERATE AUDIO
# -------------------------
def generate_audio(text, engine):
    clean = clean_text(text)
    filename = f"audio_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(AUDIO_FOLDER, filename)

    if engine == 'edge':
        async def produce_edge():
            communicate = edge_tts.Communicate(clean, "de-DE-KillianNeural")
            await communicate.save(filepath)
        
        try:
            # Intentamos usar Edge-TTS
            asyncio.run(produce_edge())
        except Exception as e:
            # Si hay error de red (como el WinError 64), usamos Google de respaldo
            print(f"⚠️ Error de conexión con Edge-TTS: {e}. Usando Google como respaldo...")
            tts = gTTS(clean, lang="de")
            tts.save(filepath)
    else:
        # Uso directo de Google gTTS
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
def save_drill(text, engine):
    #clean, audio_path = generate_audio(text)
    # generate_audio ahora recibe el motor
    clean, audio_path = generate_audio(text, engine)

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
# GENERADOR INTELIGENTE (Sustituye al anterior)
# -------------------------
def generate_drills_ai(n=10, tema="situaciones cotidianas"):
    model_name = "gemma2"
   
    # Lista de verbos que exigen Dativ + Akkusativ para guiar al modelo
    prompt = f"""
    [INSTRUCTION]
    Genera exactamente {n} frases en alemán (nivel A1-A2) sobre {tema}.
    
    [RULES]
    1. Estructura: Sujeto + Verbo + Objeto Dativo + Objeto Acusativo.
    2. Usa posesivos (mein, dein, sein, unser).
    3. Revisa la declinación: 'meinem' (M/N Dat), 'meiner' (F Dat), 'meinen' (M Akk).
    4. Sin números, sin traducciones. Solo una frase por línea.
    """

    try:
        response = ollama.chat(model=model_name, messages=[
            {'role': 'user', 'content': prompt},
        ])
        
        raw_text = response['message']['content']
        print("--- RESPUESTA DE MISTRAL ---")
        print(raw_text)
        print("----------------------------")
        
        # Limpieza robusta: elimina números, traducciones entre paréntesis y espacios extra
        lines = raw_text.split('\n')
        drills = []
        for line in lines:
            if line.strip():
                # Elimina numeración inicial (ej: "1. ")
                clean_line = re.sub(r'^\d+[\.\)]\s*', '', line)
                # Elimina cualquier cosa entre paréntesis (traducciones)
                clean_line = re.sub(r'\(.*?\)', '', clean_line).strip()
                if clean_line:
                    drills.append(clean_line)
        
        return drills
    except Exception as e:
        print(f"Error con Ollama: {e}")
        return ["Ich gebe 🟣🔵meinem Computer 🟡🔴eine Aufgabe."]



# -------------------------
# ROUTES
# -------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        content = request.form.get("content")
        # Capturamos el motor (por defecto 'edge')
        engine = request.form.get("engine", "edge")

        lines = [line.strip() for line in content.split("\n") if line.strip()]

        for line in lines:
            # Ahora pasamos el motor a save_drill
            save_drill(line, engine)

        return redirect(url_for("index"))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, audio_path FROM drills ORDER BY id DESC LIMIT 50")
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

# -------------------------
# ROUTES (Actualizada)
# -------------------------
@app.route("/generate")
def generate():
    # Obtenemos el motor de los parámetros de la URL o usamos 'edge' por defecto
    engine = request.args.get("engine", "edge")
    
    # Recuperamos un tema opcional si quieres añadir un input de texto después
    tema = request.args.get("tema", "vida diaria en Alemania")
    
    # Llamamos a la IA en lugar de la función random
    drills = generate_drills_ai(n=10, tema=tema)

    for d in drills:
        # La función save_drill ya se encarga de limpiar el texto y generar el audio 
        save_drill(d, engine)

    return redirect(url_for("index"))


# -------------------------
# RUN (COMPATIBLE CON RENDER)
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)