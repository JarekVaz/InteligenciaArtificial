import cv2 as cv
import numpy as np
import os

# Obtener la ruta absoluta del archivo imagen en la misma carpeta que este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(BASE_DIR, 'figura.png') # Ruta de la imagen

img = cv.imread(img_path, 1) # Cargar la imagen
if img is None:
    print(f"❌ Error: No se pudo cargar la imagen desde: {img_path}")
    print(f"   Verifica que 'figura.png' esté en la carpeta: {BASE_DIR}")
    exit()
    
img2 = cv.cvtColor(img, cv.COLOR_BGR2RGB) 
img3 = cv.cvtColor(img2, cv.COLOR_RGB2HSV) 
img_final = img.copy() 

umbralBajo_R=(0, 100, 100)
umbralAlto_R=(10, 255, 255)
umbralBajoB_R=(160, 100, 100)
umbralAltoB_R=(180, 255, 255)
mascara1_R = cv.inRange(img3, umbralBajo_R, umbralAlto_R)
mascara2_R = cv.inRange(img3, umbralBajoB_R, umbralAltoB_R)
mascara_R = mascara1_R + mascara2_R
contornos_R, _ = cv.findContours(mascara_R, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
contador_R = 0
for c in contornos_R:
    if cv.contourArea(c) > 100: 
        contador_R += 1
print(f"Figuras ROJAS: {contador_R}")

umbralBajo_V = (35, 100, 100)
umbralAlto_V = (85, 255, 255)
mascara_V = cv.inRange(img3, umbralBajo_V, umbralAlto_V)
contornos_V, _ = cv.findContours(mascara_V, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
contador_V = 0
for c in contornos_V:
    if cv.contourArea(c) > 100: 
        contador_V += 1
print(f"Figuras VERDES: {contador_V}")
umbralBajo_A = (100, 100, 100)
umbralAlto_A = (140, 255, 255)

mascara_A = cv.inRange(img3, umbralBajo_A, umbralAlto_A)
contornos_A, _ = cv.findContours(mascara_A, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
contador_A = 0
for c in contornos_A:
    if cv.contourArea(c) > 100: 
        contador_A += 1
print(f"Figuras AZULES: {contador_A}")

umbralBajo_Am = (15, 100, 100)
umbralAlto_Am = (35, 255, 255)
mascara_Am = cv.inRange(img3, umbralBajo_Am, umbralAlto_Am)
contornos_Am, _ = cv.findContours(mascara_Am, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
contador_Am = 0
for c in contornos_Am:
    if cv.contourArea(c) > 100: 
        contador_Am += 1
print(f"Figuras AMARILLAS: {contador_Am}")

cv.imshow('Figuras', img_final)
cv.imshow('Mascara ROJO', mascara_R) 
cv.imshow('Mascara VERDE', mascara_V) 
cv.imshow('Mascara Azul', mascara_A) 
cv.imshow('Mascara Amarilla', mascara_Am) 

cv.waitKey(0)
cv.destroyAllWindows()