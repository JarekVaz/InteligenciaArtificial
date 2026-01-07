import pandas as pd
from pathlib import Path

# Detectar ruta del dataset relativa a este script
script_dir = Path(__file__).resolve().parent
csv_path = script_dir / 'corpus_genz_multifuente.csv'
xlsx_path = script_dir / 'corpus_genz_multifuente.xlsx'

if csv_path.exists():
    df = pd.read_csv(csv_path)
elif xlsx_path.exists():
    df = pd.read_excel(xlsx_path)
else:
    raise FileNotFoundError(
        f"No se encontró 'corpus_genz_multifuente.csv' ni 'corpus_genz_multifuente.xlsx' en {script_dir}"
    )

# Limpieza básica
df['texto'] = df['texto'].str.strip().str.replace(r'\s+', ' ', regex=True)

# Crear un formato narrativo para que el RAG entienda el contexto de cada fila
df['narrativa'] = (
    "Fuente: " + df['fuente'].astype(str) + ". " +
    df['texto']
)

# Guardar como TXT para AnythingLLM en la misma carpeta del script
out_path = script_dir / 'corpus_genz_multifuente_limpio.txt'
with open(out_path, 'w', encoding='utf-8') as f:
    for linea in df['narrativa']:
        f.write(linea + "\n---\n")

print(f"Salida guardada en: {out_path}")