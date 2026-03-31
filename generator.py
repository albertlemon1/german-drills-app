import random

# -------------------------
# DATOS
# -------------------------

nouns = [
    {"word": "Vater", "gender": "m"},
    {"word": "Mutter", "gender": "f"},
    {"word": "Kind", "gender": "n"},
    {"word": "Freund", "gender": "m"},
    {"word": "Tasche", "gender": "f"},
    {"word": "Auto", "gender": "n"},
]

verbs_akk = ["sehen", "finden", "kaufen", "lieben"]
verbs_dat_akk = ["geben", "zeigen", "bringen"]

subjects = [
    ("Ich", "mein"),
    ("Du", "dein"),
    ("Er", "sein"),
    ("Sie", "ihr"),
    ("Wir", "unser"),
    ("Ihr", "euer"),
    ("Sie (pl)", "ihr")
]

# -------------------------
# DECLINACIÓN SIMPLE
# -------------------------

def decline_possessive(base, gender, case):
    if case == "akk":
        if gender == "m":
            return base + "en"
        if gender == "f":
            return base + "e"
        if gender == "n":
            return base
    if case == "dat":
        if gender == "m":
            return base + "em"
        if gender == "f":
            return base + "er"
        if gender == "n":
            return base + "em"

def color(gender, case):
    g = {"m": "🔵", "f": "🔴", "n": "🟢"}[gender]
    c = "🟡" if case == "akk" else "🟣"
    return c + g

# -------------------------
# GENERADOR DE FRASES
# -------------------------

def generate_sentence():
    subj, poss = random.choice(subjects)
    noun = random.choice(nouns)

    # 50% Akk / 50% Dat+Ak
    if random.random() < 0.5:
        verb = random.choice(verbs_akk)
        case = "akk"

        poss_declined = decline_possessive(poss, noun["gender"], case)
        return f"{subj} {verb} {color(noun['gender'], case)}{poss_declined} {noun['word']}"

    else:
        verb = random.choice(verbs_dat_akk)

        noun_dat = random.choice(nouns)
        noun_akk = random.choice(nouns)

        poss_dat = decline_possessive(poss, noun_dat["gender"], "dat")
        poss_akk = decline_possessive(poss, noun_akk["gender"], "akk")

        return f"{subj} {verb} {color(noun_dat['gender'],'dat')}{poss_dat} {noun_dat['word']} {color(noun_akk['gender'],'akk')}{poss_akk} {noun_akk['word']}"

# -------------------------
# DRILL COMPLETO
# -------------------------

def generate_drill(n=20):
    lines = [generate_sentence() for _ in range(n)]

    html = "<h3>DRILL (20 EJEMPLOS COMPLETOS)</h3>"
    html += "<p><b>🔹 Parte 1: Ejemplos en alemán</b></p>"

    for l in lines:
        html += l + "<br>"

    return html

def generate_story():
    templates = [
        "Ich reise gern, weil ich {akk} sehe.",
        "Wir geben {dat} {akk}.",
        "Ein Freund zeigt {dat} {akk}.",
        "Ich finde {akk} sehr interessant.",
    ]

    story = "<h3>5 HISTORIAS (con código aplicado)</h3>"

    for i in range(5):
        story += f"<h4>Historia {i+1}</h4>"

        for _ in range(3):
            sentence = generate_sentence()
            story += sentence + "<br>"

    return story