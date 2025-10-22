import cv2 as cv
import os
import json
import sys

# Rutas robustas basadas en la ubicación del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
base_name = os.path.basename(BASE_DIR).lower()
if base_name == 'caras':
    caras_dir = BASE_DIR
else:
    caras_dir = os.path.join(BASE_DIR, 'Caras')

model_path = os.path.join(caras_dir, 'Eigenface.xml')
cascade_path = os.path.join(caras_dir, 'haarcascade_frontalface_alt.xml')
labels_path = os.path.join(caras_dir, 'labels.json')

# Verificaciones básicas
if not hasattr(cv, 'face'):
    print('Error: el módulo cv2.face no está disponible. Instala opencv-contrib-python.')
    sys.exit(1)

if not os.path.exists(cascade_path):
    print(f'Error: no se encontró el cascade en: {cascade_path}')
    sys.exit(1)

if not os.path.exists(model_path):
    print(f'Error: no se encontró el modelo en: {model_path}')
    sys.exit(1)

# Cargar recognizer
faceRecognizer = cv.face.EigenFaceRecognizer_create()
faceRecognizer.read(model_path)

# Cargar labels.json (si existe) o usar fallback
labels_map = {}
if os.path.exists(labels_path):
    try:
        with open(labels_path, 'r', encoding='utf-8') as f:
            lm = json.load(f)
        # convertir keys a int
        labels_map = {int(k): v for k, v in lm.items()}
        print(f'✓ labels cargados desde: {labels_path}')
    except Exception as e:
        print(f'⚠️  No se pudo leer labels.json: {e}')

# Abrir cámara y cascade
cap = cv.VideoCapture(0)
if not cap.isOpened():
    print('Error: no se pudo abrir la cámara (device 0).')
    sys.exit(1)
rostro = cv.CascadeClassifier(cascade_path)

# Umbral: para EigenFace/Fisher la "confidence" es distancia (menor = mejor).
# Ajusta este valor según tus pruebas. Valor inicial sugerido: 2800
THRESHOLD = 2800

print('Iniciando detección. Presiona ESC para salir.')
while True:
    ret, frame = cap.read()
    if not ret:
        print('Error: no se recibió frame de la cámara.')
        break

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    cpGray = gray.copy()
    rostros = rostro.detectMultiScale(gray, 1.3, 3)
    for (x, y, w, h) in rostros:
        roi = cpGray[y:y+h, x:x+w]
        try:
            roi_resized = cv.resize(roi, (100, 100), interpolation=cv.INTER_CUBIC)
        except Exception:
            continue

        try:
            result = faceRecognizer.predict(roi_resized)
            label, confidence = result[0], result[1]
        except Exception as e:
            # Si predict falla, marcar como desconocido
            label, confidence = None, None
            print(f'⚠️  predict falló: {e}')

        name = 'Desconocido'
        color = (0, 0, 255)  # rojo
        if label is not None and confidence is not None:
            # Si hay labels_map, usarlo
            if labels_map:
                name = labels_map.get(label, 'Desconocido')
            else:
                name = str(label)

            # Para EigenFace: menor distancia => más parecido
            if confidence < THRESHOLD:
                color = (0, 255, 0)  # verde
            else:
                color = (0, 0, 255)

        # Mostrar nombre y confianza (si disponible)
        label_text = f"{name}"
        if confidence is not None:
            label_text += f" {confidence:.1f}"

        cv.putText(frame, label_text, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    cv.imshow('frame', frame)
    k = cv.waitKey(1) & 0xFF
    if k == 27:
        break

cap.release()
cv.destroyAllWindows()