import sys
import math
from queue import PriorityQueue
from typing import Dict, List, Optional, Tuple

import pygame

pygame.init()

# Configuraciones iniciales
ANCHO, ALTO = 900, 640
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Programa A*")

# Áreas derivadas (grid proporcional al tamaño de ventana)
GRID_RATIO = 0.7
PANEL_MIN_ANCHO = 220
tam_grilla = int(ANCHO * GRID_RATIO)
tam_grilla = min(tam_grilla, ALTO)
tam_grilla = min(tam_grilla, ANCHO - PANEL_MIN_ANCHO)
if tam_grilla < 200:
    tam_grilla = max(ANCHO - PANEL_MIN_ANCHO, 200)
    tam_grilla = min(tam_grilla, ALTO)
ANCHO_GRID = tam_grilla
PANEL_ANCHO = ANCHO - ANCHO_GRID
FUENTE = pygame.font.SysFont("Arial", 16)
FUENTE_PANEL = pygame.font.SysFont("Arial", 18)
FUENTE_CELDA = pygame.font.SysFont("Arial", 12)
FUENTE_FGH = pygame.font.SysFont("Arial", 10)

# Colores (RGB)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
GRIS = (128, 128, 128)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
NARANJA = (255, 165, 0)
PURPURA = (128, 0, 128)
CIAN = (64, 224, 208)

# Costes (como en asterisco.py)
COST_ARR_ABA = 10
COST_DIAG = 14

INSTRUCCIONES_PANEL: List[str] = [
    "Instrucciones",
    "- Click izquierdo: inicio/fin/pared",
    "- Click derecho: limpiar celda",
    "- Espacio: Ejecutar A*",
    "- Enter: reiniciar tablero",
]


class Nodo:
    def __init__(self, fila: int, col: int, ancho: int, total_filas: int):
        self.fila = fila
        self.col = col
        self.x = fila * ancho
        self.y = col * ancho
        self.color = BLANCO
        self.ancho = ancho
        self.total_filas = total_filas
        self.vecinos: List["Nodo"] = []
        self.g = float('inf')
        self.h = float('inf')
        self.f = float('inf')

    def __lt__(self, other):
        return False

    def __eq__(self, other):
        return isinstance(other, Nodo) and (self.fila, self.col) == (other.fila, other.col)

    def __hash__(self):
        return hash((self.fila, self.col))

    def get_pos(self) -> Tuple[int, int]:
        return self.fila, self.col

    def es_pared(self) -> bool:
        return self.color == NEGRO

    def es_inicio(self) -> bool:
        return self.color == NARANJA

    def es_fin(self) -> bool:
        return self.color == PURPURA

    def restablecer(self) -> None:
        self.color = BLANCO
        self.g = float('inf')
        self.h = float('inf')
        self.f = float('inf')

    def hacer_inicio(self) -> None:
        self.color = NARANJA

    def hacer_pared(self) -> None:
        self.color = NEGRO

    def hacer_fin(self) -> None:
        self.color = PURPURA

    def hacer_abierto(self) -> None:
        self.color = VERDE

    def hacer_cerrado(self) -> None:
        self.color = ROJO

    def hacer_camino(self) -> None:
        self.color = CIAN

    def dibujar(self, ventana: pygame.Surface) -> None:
        pygame.draw.rect(ventana, self.color, (self.x, self.y, self.ancho, self.ancho))
        etiqueta = etiquetar_posicion((self.fila, self.col))
        texto_color = BLANCO if sum(self.color) < 300 else NEGRO
        # Etiqueta en la esquina superior izquierda
        texto = FUENTE_CELDA.render(etiqueta, True, texto_color)
        ventana.blit(texto, (self.x + 2, self.y + 2))
        # Mostrar f, g, h alineados a la derecha del cuadro con fuente pequeña
        # Solo mostrar cuando los valores sean finitos (evitar int(inf))
        if math.isfinite(self.f) and math.isfinite(self.g) and math.isfinite(self.h):
            f_text = FUENTE_FGH.render(f"f:{int(self.f)}", True, texto_color)
            g_text = FUENTE_FGH.render(f"g:{int(self.g)}", True, texto_color)
            h_text = FUENTE_FGH.render(f"h:{int(self.h)}", True, texto_color)
            spacing = 2
            # Alinear a la derecha, dejando un pequeño margen
            right_x = self.x + self.ancho - f_text.get_width() - 2
            start_y = self.y + 4
            ventana.blit(f_text, (right_x, start_y))
            ventana.blit(g_text, (right_x, start_y + f_text.get_height() + spacing))
            ventana.blit(h_text, (right_x, start_y + f_text.get_height() + g_text.get_height() + 2 * spacing))

    def actualizar_vecinos(self, grid: List[List["Nodo"]]):
        self.vecinos = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r = self.fila + dr
                c = self.col + dc
                if 0 <= r < self.total_filas and 0 <= c < self.total_filas:
                    if not grid[r][c].es_pared():
                        self.vecinos.append(grid[r][c])


def crear_grid(filas: int, ancho: int) -> List[List[Nodo]]:
    grid: List[List[Nodo]] = []
    ancho_nodo = ancho // filas
    for i in range(filas):
        grid.append([])
        for j in range(filas):
            nodo = Nodo(i, j, ancho_nodo, filas)
            grid[i].append(nodo)
    return grid


def dibujar_grid(ventana: pygame.Surface, filas: int, ancho: int) -> None:
    ancho_nodo = ancho // filas
    for i in range(filas + 1):
        pygame.draw.line(ventana, GRIS, (0, i * ancho_nodo), (ancho, i * ancho_nodo))
        pygame.draw.line(ventana, GRIS, (i * ancho_nodo, 0), (i * ancho_nodo, ancho))


def dibujar_panel(ventana: pygame.Surface,
                 lista_cerrada: Optional[List[Tuple[int, int]]],
                 exito: Optional[bool],
                 camino: Optional[List[Tuple[int, int]]]) -> None:
    panel_rect = pygame.Rect(ANCHO_GRID, 0, PANEL_ANCHO, ALTO)
    pygame.draw.rect(ventana, (240, 240, 240), panel_rect)
    pygame.draw.line(ventana, GRIS, (ANCHO_GRID, 0), (ANCHO_GRID, ALTO))

    x = ANCHO_GRID + 16
    y = 20
    for indice, texto in enumerate(INSTRUCCIONES_PANEL):
        fuente = FUENTE_PANEL if indice == 0 else FUENTE
        superficie = fuente.render(texto, True, NEGRO)
        ventana.blit(superficie, (x, y))
        y += 30 if indice == 0 else 22

    y += 10
    ventana.blit(FUENTE_PANEL.render("Resultados", True, NEGRO), (x, y))
    y += 30

    if lista_cerrada is None:
        mensaje = "Presiona Espacio para ejecutar A*"
        ventana.blit(FUENTE.render(mensaje, True, NEGRO), (x, y))
        return

    estado = "Camino óptimo encontrado" if exito else "No se encontró camino"
    ventana.blit(FUENTE.render(estado, True, NEGRO), (x, y))
    y += 24

    if exito and camino:
        pasos = len(camino) - 1
        ventana.blit(FUENTE.render(f"Longitud: {pasos} pasos", True, NEGRO), (x, y))
        y += 20
        camino_lineas = formatear_camino(camino, ancho=3)
        for indice, linea in enumerate(camino_lineas):
            prefijo = "Camino:" if indice == 0 else ""
            texto_linea = f"{prefijo} {linea}".strip()
            ventana.blit(FUENTE.render(texto_linea, True, NEGRO), (x, y))
            y += 20
        y += 6

    ventana.blit(FUENTE.render("Lista cerrada:", True, NEGRO), (x, y))
    y += 22
    for linea in formatear_lista_cerrada(lista_cerrada, ancho=4):
        superficie = FUENTE.render(linea, True, NEGRO)
        ventana.blit(superficie, (x, y))
        y += 18


def dibujar(ventana: pygame.Surface, grid: List[List[Nodo]], filas: int, ancho: int,
            lista_cerrada: Optional[List[Tuple[int, int]]] = None,
            exito: Optional[bool] = None,
            camino: Optional[List[Tuple[int, int]]] = None) -> None:
    ventana.fill(BLANCO)
    for fila in grid:
        for nodo in fila:
            nodo.dibujar(ventana)

    dibujar_grid(ventana, filas, ancho)
    dibujar_panel(ventana, lista_cerrada, exito, camino)

    pygame.display.update()


def obtener_click_pos(pos: Tuple[int, int], filas: int, ancho: int) -> Tuple[int, int]:
    ancho_nodo = ancho // filas
    y, x = pos
    fila = y // ancho_nodo
    col = x // ancho_nodo
    return fila, col


def heuristica(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    # Distancia octil para movimiento diagonal (usando costes enteros como en asterisco.py)
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    D = COST_ARR_ABA
    D2 = COST_DIAG
    return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)


def etiquetar_posicion(posicion: Tuple[int, int]) -> str:
    fila, col = posicion
    if col < 26:
        etiqueta_col = chr(ord("A") + col)
    else:
        etiqueta_col = f"C{col + 1}"
    return f"{etiqueta_col}{fila + 1}"


def reconstruir_camino(origenes: Dict[Nodo, Nodo], destino: Nodo) -> List[Nodo]:
    camino = [destino]
    actual = destino
    while actual in origenes:
        actual = origenes[actual]
        camino.append(actual)
    camino.reverse()
    return camino


def formatear_lista_cerrada(cerrada: List[Tuple[int, int]], ancho: int = 6) -> List[str]:
    bloques: List[str] = []
    linea: List[str] = []
    for indice, nodo in enumerate(cerrada, start=1):
        linea.append(etiquetar_posicion(nodo))
        if indice % ancho == 0:
            bloques.append(", ".join(linea))
            linea = []
    if linea:
        bloques.append(", ".join(linea))
    if not bloques:
        bloques.append("Lista cerrada vacía")
    return bloques


def formatear_camino(camino: List[Tuple[int, int]], ancho: int = 6) -> List[str]:
    if not camino:
        return []
    bloques: List[str] = []
    linea: List[str] = []
    for indice, nodo in enumerate(camino, start=1):
        linea.append(etiquetar_posicion(nodo))
        if indice % ancho == 0:
            bloques.append(" -> ".join(linea))
            linea = []
    if linea:
        bloques.append(" -> ".join(linea))
    return bloques


def mostrar_resultados_consola(exito: bool, camino: List[Tuple[int, int]],
                               cerrada: List[Tuple[int, int]]) -> None:
    print("\n=== Resultado de A* ===")
    print(f"Camino óptimo encontrado: {'Sí' if exito else 'No'}")
    if exito and camino:
        pasos = len(camino) - 1
        print(f"Longitud del camino: {pasos} pasos")
        print("Camino óptimo:")
        for linea in formatear_camino(camino):
            print(f"   {linea}")
    print(f"Lista cerrada ({len(cerrada)} nodos):")
    # Mostrar como array de etiquetas algebraicas
    etiquetas = [etiquetar_posicion(pos) for pos in cerrada]
    print(etiquetas)
    print()


def heuristica_octile(p1, p2):
    (r1, c1) = p1
    (r2, c2) = p2
    dx = abs(c1 - c2)
    dy = abs(r1 - r2)
    D = COST_ARR_ABA
    D2 = COST_DIAG
    return D*(dx+dy) + (D2 - 2*D)*min(dx, dy)


def reconstruir_camino(came_from, actual, draw):
    while actual in came_from:
        actual = came_from[actual]
        if not actual.es_inicio() and not actual.es_fin():
            actual.hacer_camino()
        draw()


def a_estrella(draw, grid, inicio, fin):
    # Implementación basada en algoritmo de asterisco.py (Itzel)
    for fila in grid:
        for nodo in fila:
            nodo.g = nodo.h = nodo.f = float('inf')

    contador = 0
    open_set = PriorityQueue()
    inicio.g = 0
    inicio.h = heuristica_octile(inicio.get_pos(), fin.get_pos())
    inicio.f = inicio.g + inicio.h

    open_set.put((inicio.f, inicio.h, contador, inicio))
    open_set_hash = {inicio}
    came_from = {}
    lista_abierta = []
    lista_cerrada = []
    camino_optimo = []

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Guardar snapshot de la lista abierta
        la_snapshot = [(nodo.fila, nodo.col) for _, _, _, nodo in open_set.queue if nodo in open_set_hash]
        lista_abierta.append(list(la_snapshot))

        _, _, _, current = open_set.get()

        if current not in open_set_hash:
            continue
        open_set_hash.remove(current)
        lista_cerrada.append((current.fila, current.col))

        if not current.es_inicio():
            current.hacer_cerrado()

        if current == fin:
            temp = current
            while temp in came_from:
                camino_optimo.append((temp.fila, temp.col))
                temp = came_from[temp]
            camino_optimo.append((inicio.fila, inicio.col))
            camino_optimo.reverse()
            reconstruir_camino(came_from, fin, draw)
            inicio.hacer_inicio()
            fin.hacer_fin()
            # Mostrar en consola (como en asterisco.py)
            print("\n--- Lista abierta (por expansión) ---")
            for i, la in enumerate(lista_abierta):
                print(f"Expansión {i+1}: {la}")
            print("\n--- Lista cerrada (orden de expansión) ---")
            print(lista_cerrada)
            print("\n--- Camino óptimo ---")
            print(camino_optimo)
            return True, lista_cerrada, camino_optimo

        for vecino in current.vecinos:
            dr = abs(vecino.fila - current.fila)
            dc = abs(vecino.col - current.col)
            move_cost = COST_DIAG if dr == 1 and dc == 1 else COST_ARR_ABA

            tentative_g = current.g + move_cost
            if tentative_g < vecino.g:
                came_from[vecino] = current
                vecino.g = tentative_g
                vecino.h = heuristica_octile(vecino.get_pos(), fin.get_pos())
                vecino.f = vecino.g + vecino.h

                if vecino not in open_set_hash:
                    contador += 1
                    open_set.put((vecino.f, vecino.h, contador, vecino))
                    open_set_hash.add(vecino)
                    if not vecino.es_fin():
                        vecino.hacer_abierto()

        draw()

    print("No se encontró camino.")
    return False, lista_cerrada, []


def main(ventana: pygame.Surface, ancho_grid: int) -> None:
    filas = 11
    grid = crear_grid(filas, ancho_grid)
    inicio: Optional[Nodo] = None
    fin: Optional[Nodo] = None
    lista_cerrada: Optional[List[Tuple[int, int]]] = None
    exito: Optional[bool] = None
    camino_optimo: Optional[List[Tuple[int, int]]] = None

    corriendo = True
    while corriendo:
        dibujar(ventana, grid, filas, ancho_grid, lista_cerrada, exito, camino_optimo)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                corriendo = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if pos[0] >= ANCHO_GRID or pos[1] >= ANCHO_GRID:
                    continue
                fila, col = obtener_click_pos(pos, filas, ancho_grid)
                nodo = grid[fila][col]
                if not inicio and nodo != fin:
                    inicio = nodo
                    inicio.hacer_inicio()
                elif not fin and nodo != inicio:
                    fin = nodo
                    fin.hacer_fin()
                elif nodo != fin and nodo != inicio:
                    nodo.hacer_pared()
                lista_cerrada = None
                exito = None
                camino_optimo = None

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                if pos[0] >= ANCHO_GRID or pos[1] >= ANCHO_GRID:
                    continue
                fila, col = obtener_click_pos(pos, filas, ancho_grid)
                nodo = grid[fila][col]
                nodo.restablecer()
                if nodo == inicio:
                    inicio = None
                if nodo == fin:
                    fin = None
                lista_cerrada = None
                exito = None
                camino_optimo = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    corriendo = False
                    break
                if event.key == pygame.K_SPACE and inicio and fin:
                    for fila in grid:
                        for nodo in fila:
                            nodo.actualizar_vecinos(grid)
                    resultado, cerrada, camino = a_estrella(
                        lambda: dibujar(ventana, grid, filas, ancho_grid), grid, inicio, fin
                    )
                    lista_cerrada = cerrada
                    exito = resultado
                    camino_optimo = camino if resultado else None
                    mostrar_resultados_consola(resultado, camino, cerrada)
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    grid = crear_grid(filas, ancho_grid)
                    inicio = None
                    fin = None
                    lista_cerrada = None
                    exito = None
                    camino_optimo = None

    pygame.quit()


if __name__ == "__main__":
    main(VENTANA, ANCHO_GRID)