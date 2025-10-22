#Este codigo hace la clasificacion de las caras guardadas en la carpeta Rostros


#https://github.com/opencv/opencv   Kaggle data sets de caras de alguien trsite , enojado o feliz 5 mil por emocion
import cv2 as cv 
import numpy as np 
import os
import json

# Ruta base del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Detectar si el script está dentro de la carpeta 'Caras' para construir rutas sin duplicar
base_name = os.path.basename(BASE_DIR).lower()
if base_name == 'caras':
    caras_dir = BASE_DIR
    dataSet = os.path.join(caras_dir, 'Rostros')
    project_root = os.path.abspath(os.path.join(BASE_DIR, '..'))
else:
    caras_dir = os.path.join(BASE_DIR, 'Caras')
    dataSet = os.path.join(BASE_DIR, 'Caras', 'Rostros')
    project_root = BASE_DIR

# Verificar que la carpeta existe
if not os.path.isdir(dataSet):
    print(f"❌ Error: No se encontró la carpeta de dataset: {dataSet}")
    print(f"   Asegúrate de tener carpetas con nombres de personas dentro de Caras/Rostros/")
    exit()

faces  = os.listdir(dataSet)
print(f"Carpetas encontradas: {faces}")

labels = []
facesData = []
label = 0 
label_map = {}  # mapeo label -> nombre
counts = {}
for face in faces:
    facePath = os.path.join(dataSet, face)

    # Ignorar archivos que no sean carpetas
    if not os.path.isdir(facePath):
        print(f"⚠️  Ignorando archivo: {face}")
        continue

    print(f"Procesando persona: {face} (label={label})")
    label_map[str(label)] = face
    counts[face] = 0
    for faceName in os.listdir(facePath):
        img_path = os.path.join(facePath, faceName)

        # Ignorar si no es un archivo
        if not os.path.isfile(img_path):
            continue

        # Leer la imagen en escala de grises y validar
        img = cv.imread(img_path, 0)
        if img is None:
            print(f"⚠️  No se pudo leer la imagen: {img_path}")
            continue

        # Asegurar tamaño uniforme (redimensionar a 100x100 si es necesario)
        try:
            img = cv.resize(img, (100, 100), interpolation=cv.INTER_AREA)
        except Exception:
            # Si falla el resize, omitir la imagen
            print(f"⚠️  Error al redimensionar: {img_path}")
            continue

        labels.append(label)
        facesData.append(img)
        counts[face] += 1
    label = label + 1

# Mostrar conteos por persona
print("\nConteo de imágenes por persona:")
for name, cnt in counts.items():
    print(f" - {name}: {cnt}")

print(f"Total de imágenes cargadas: {len(facesData)}")

# Guardar el mapeo label -> nombre en labels.json dentro de la carpeta Caras
os.makedirs(caras_dir, exist_ok=True)
labels_json_path = os.path.join(caras_dir, 'labels.json')
with open(labels_json_path, 'w', encoding='utf-8') as f:
    json.dump(label_map, f, ensure_ascii=False, indent=2)
print(f"✓ labels.json guardado en: {labels_json_path}")

# Crear el recognizer (EigenFace)
faceRecognizer = cv.face.EigenFaceRecognizer_create()
# Reemplaza EigenFaceRecognizer por LBPHFaceRecognizer
#faceRecognizer = cv.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
# No olvides cambiar el nombre del archivo XML si quieres: faceRecognizer.write('LBPH.xml')
print("Entrenando el modelo...")
faceRecognizer.train(facesData, np.array(labels))

# Guardar el modelo en la raíz del proyecto
# Guardar el modelo dentro de la carpeta Caras (mantener artefactos juntos)
model_path = os.path.join(caras_dir, 'Eigenface.xml')

# Buscar modelo antiguo en project_root y en BASE_DIR y moverlo a Caras para mantener orden
old_model_candidates = [
    os.path.join(project_root, 'Eigenface.xml'),
    os.path.join(BASE_DIR, 'Eigenface.xml')
]
for old_model in old_model_candidates:
    if os.path.exists(old_model) and not os.path.exists(model_path):
        try:
            os.replace(old_model, model_path)
            print(f"✓ Modelo existente movido desde {old_model} a {model_path}")
            break
        except Exception as e:
            print(f"⚠️  No se pudo mover el modelo existente desde {old_model}: {e}")

faceRecognizer.write(model_path)
print(f"✓ Modelo entrenado y guardado en: {model_path}")