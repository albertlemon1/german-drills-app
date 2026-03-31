import sqlite3

conn = sqlite3.connect("grammar.db")
cursor = conn.cursor()

# =========================
# TABLA SUSTANTIVOS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS nouns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT,
    article TEXT,
    gender TEXT
)
""")

# =========================
# TABLA VERBOS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS verbs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verb TEXT,
    case_type TEXT
)
""")

# =========================
# INSERTAR SUSTANTIVOS
# =========================
nouns = [
    ("Vater", "der", "masc"),
    ("Freund", "der", "masc"),
    ("Mutter", "die", "fem"),
    ("Tasche", "die", "fem"),
    ("Kind", "das", "neut"),
    ("Auto", "das", "neut")
]

cursor.executemany(
    "INSERT INTO nouns (word, article, gender) VALUES (?, ?, ?)",
    nouns
)

# =========================
# VERBOS DATIV + AKK (30)
# =========================
dativ_verbs = [
    "geben", "bringen", "zeigen", "schenken", "erklären",
    "leihen", "schicken", "kaufen", "verkaufen", "sagen",
    "erzählen", "empfehlen", "anbieten", "vorstellen",
    "überreichen", "reichen", "gewähren", "beantworten",
    "übermitteln", "zustellen", "mitteilen", "vermitteln",
    "übergeben", "zuschicken", "zurückgeben", "spenden",
    "widmen", "verleihen", "überlassen", "bereitstellen"
]

# =========================
# VERBOS SOLO AKK (30)
# =========================
akk_verbs = [
    "sehen", "finden", "lieben", "hören", "kaufen",
    "besuchen", "treffen", "brauchen", "nehmen", "kennen",
    "lernen", "fragen", "suchen", "haben", "bekommen",
    "öffnen", "schließen", "lesen", "schreiben", "essen",
    "trinken", "vergessen", "verstehen", "holen", "bringen",
    "legen", "stellen", "benutzen", "wählen", "bezahlen"
]

# INSERT
cursor.executemany(
    "INSERT INTO verbs (verb, case_type) VALUES (?, ?)",
    [(v, "dativ_akk") for v in dativ_verbs]
)

cursor.executemany(
    "INSERT INTO verbs (verb, case_type) VALUES (?, ?)",
    [(v, "akk") for v in akk_verbs]
)

conn.commit()
conn.close()

print("✅ Base de datos creada")