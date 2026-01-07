import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import subprocess
import json
import os

# =========================
# CONFIGURACIÓN GENERAL
# =========================

MAX_TEXTOS_POR_FUENTE = 200
SALIDA = "corpus_genz_multifuente.csv"

# =========================
# FUNCIÓN DE LIMPIEZA
# =========================

def limpiar_texto(texto):
    texto = re.sub(r"http\S+", "", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()

corpus = []

# ==================================================
# 1️⃣ ARTÍCULOS WEB / BLOGS
# ==================================================

urls_web = [
    # Psicología, ansiedad, identidad
    "https://www.psychologytoday.com/us/basics/generation-z",
    "https://www.psychologytoday.com/us/blog/the-anatomy-of-anxiety",
    "https://www.psychologytoday.com/us/blog/brain-wise",
    "https://www.psychologytoday.com/us/blog/modern-minds",
    "https://www.healthline.com/mental-health/anxiety",
    "https://www.healthline.com/mental-health/burnout",
    "https://www.healthline.com/mental-health/social-media-anxiety",
    "https://www.verywellmind.com/generation-z-mental-health-5189670",

    # Generación Z, trabajo, burnout
    "https://www.forbes.com/sites/forbescoachescouncil/tag/generation-z/",
    "https://www.forbes.com/sites/ashleystahl/2023/05/22/gen-z-burnout/",
    "https://hbr.org/2023/01/gen-zs-mental-health-crisis",
    "https://hbr.org/2022/07/what-gen-z-wants-from-work",
    "https://www.weforum.org/agenda/2023/01/gen-z-mental-health/",

    # Redes sociales, algoritmos y tecnología
    "https://www.theguardian.com/technology/social-media",
    "https://www.theguardian.com/commentisfree",
    "https://www.wired.com/tag/algorithms/",
    "https://www.wired.com/tag/social-media/",
    "https://www.vox.com/technology",
    "https://www.vox.com/recode",
    "https://www.theatlantic.com/technology/",

    # Cultura digital, identidad
    "https://medium.com/tag/gen-z",
    "https://medium.com/tag/social-media",
    "https://medium.com/tag/mental-health",
    "https://medium.com/tag/identity",
    "https://medium.com/tag/technology",

    # Medios en español
    "https://elpais.com/noticias/generacion-z/",
    "https://elpais.com/tecnologia/",
    "https://www.bbc.com/mundo/topics/cyx5krnw38vt",
    "https://www.bbc.com/mundo/topics/cyx5krnw38vt/social-media",
    "https://www.dw.com/es/temas/s-9117",
    "https://theconversation.com/es/topics/generacion-z-20690",

    # Opinión y reflexión profunda
    "https://theconversation.com/topics/mental-health-1784",
    "https://theconversation.com/topics/social-media-1931",
    "https://theconversation.com/topics/technology-1959",
    "https://aeon.co/",
    "https://psyche.co/"
]


cont_web = 0

for url in urls_web:
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        for p in soup.find_all("p"):
            texto = limpiar_texto(p.get_text())
            if len(texto) > 120:
                corpus.append({"texto": texto, "fuente": "web"})
                cont_web += 1
            if cont_web >= MAX_TEXTOS_POR_FUENTE:
                break
    except:
        pass

# ==================================================
# 2️⃣ COMENTARIOS DE YOUTUBE (PÚBLICOS)
# ==================================================

youtube_videos = [
    "https://www.youtube.com/watch?v=8wqNX7_4vAE",
    "https://www.youtube.com/watch?v=Yx9l6U8cK5I"
]

comentarios_yt = []

for video in youtube_videos:
    try:
        cmd = [
            "yt-dlp",
            "--skip-download",
            "--write-comments",
            "--dump-single-json",
            video
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)

        for c in data.get("comments", []):
            texto = limpiar_texto(c.get("text", ""))
            if len(texto) > 80:
                comentarios_yt.append({"texto": texto, "fuente": "youtube"})
            if len(comentarios_yt) >= MAX_TEXTOS_POR_FUENTE:
                break
    except:
        pass

corpus.extend(comentarios_yt[:MAX_TEXTOS_POR_FUENTE])

# ==================================================
# 3️⃣ FOROS ABIERTOS / COMENTARIOS WEB
# ==================================================

urls_foros = [
    "https://www.psychologytoday.com/us/blog/the-anatomy-of-anxiety",
    "https://www.healthline.com/mental-health/anxiety",
]

cont_foros = 0

for url in urls_foros:
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        for p in soup.find_all("p"):
            texto = limpiar_texto(p.get_text())
            if len(texto) > 120:
                corpus.append({"texto": texto, "fuente": "foro"})
                cont_foros += 1
            if cont_foros >= MAX_TEXTOS_POR_FUENTE:
                break
    except:
        pass

# ==================================================
# DATASET FINAL
# ==================================================

df = pd.DataFrame(corpus)
df = df.drop_duplicates().reset_index(drop=True)
df.to_csv(SALIDA, index=False, encoding="utf-8")

print("✅ Corpus multifuente generado")
print(df["fuente"].value_counts())
print(f"Total de textos: {len(df)}")
