import numpy as np  # Librería numérica (no se usa directamente aquí, pero suele ser útil con OpenCV)
import cv2 as cv   # OpenCV: procesamiento de imágenes y video
import os          # Manejo de rutas y creación de carpetas


# Obtener el directorio donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Carga del clasificador Haar para detectar rostros.
# Usar ruta absoluta al archivo XML que está en la misma carpeta que este script.
cascade_path = os.path.join(BASE_DIR, 'haarcascade_frontalface_alt.xml')
rostro = cv.CascadeClassifier(cascade_path)

# Fuente de video: 0 = cámara web predeterminada.
cap = cv.VideoCapture(0) 

if not cap.isOpened():
    # Si no se pudo abrir la cámara, se muestra un mensaje y se sale del programa.
    print("Error: No se pudo acceder a la cámara. Revisa si otra aplicación la está usando.")
    exit()

# Variables auxiliares para coordenadas del rostro y contadores.
x=y=h=w=0
count = 0 
img = 0
MAX_IMAGES = 1000  # Número máximo de imágenes a guardar por sesión

# Ruta de salida: crear una carpeta única por sesión dentro de Caras/Rostros/
ROSTROS_DIR = os.path.join(BASE_DIR, 'Rostros')

# Buscar el siguiente número de sesión disponible
session_number = 1
while True:
    SESSION_DIR = os.path.join(ROSTROS_DIR, f'Sesion{session_number}')
    if not os.path.exists(SESSION_DIR):
        break
    session_number += 1

os.makedirs(SESSION_DIR, exist_ok=True)
print(f"Sesión {session_number} iniciada. Las imágenes se guardarán en: {SESSION_DIR}")

while True:
    # Captura un frame de la cámara.
    ret, frame = cap.read()
    if not ret:
        # Si no se puede leer el frame (por ejemplo, cámara desconectada), se sale del bucle.
        print("Error: No se puede recibir el frame. Saliendo...")
        break 

    # Conversión a escala de grises (mejora el rendimiento del detector).
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Detección de rostros.
    # Parámetros:
    #  - scaleFactor=1.3: cuánto reduce la imagen en cada escala.
    #  - minNeighbors=5: cuántos vecinos necesita cada rectángulo candidato para ser conservado.
    rostros = rostro.detectMultiScale(gray, 1.3, 5) 

    # Recorre cada rostro detectado.
    for(x, y, w, h) in rostros:
        # Dibuja un rectángulo verde alrededor del rostro para visualizarlo.
        frame = cv.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2)

        # Recorta la región del rostro (ROI: Region Of Interest).
        img = frame[y:y+h, x:x+w]
        
        # Redimensiona a 100x100 píxeles para mantener uniformidad en el dataset
        img = cv.resize(img, (100, 100), interpolation=cv.INTER_AREA)

        # Guarda una imagen cada 10 detecciones para no saturar el disco.
        if count % 10 == 0:
            # Guarda en la carpeta de la sesión actual: .../Rostros/sesion_AAAAMMDD_HHMMSS/face_X.jpg
            name = os.path.join(SESSION_DIR, f'face_{count}.jpg')
            cv.imwrite(name, img)
            print(f"Guardado: {name}") 

        count = count + 1
        
        # Si ya se guardaron 1000 imágenes, terminar la sesión
        if count >= MAX_IMAGES * 10:  # count * 10 porque guardamos cada 10 frames
            print(f"\n✓ Sesión completada: se alcanzó el límite de {MAX_IMAGES} imágenes guardadas.")
            break
    
    # Si se alcanzó el límite, salir del bucle principal también
    if count >= MAX_IMAGES * 10:
        break

    # Muestra el frame con las detecciones en una ventana.
    cv.imshow('Detección de Rostros', frame)

    # Si se presiona la tecla 'q', se cierra el programa.
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
        break

# Libera la cámara y cierra todas las ventanas creadas por OpenCV.
cap.release()
cv.destroyAllWindows()
