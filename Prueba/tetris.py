import pygame
import sys
import random # Necesario para elegir piezas al azar

# Inicializar Pygame
pygame.init()

# Dimensiones de la pantalla
ANCHO_PANTALLA = 300
ALTO_PANTALLA = 600
TAMANO_BLOQUE = 30

ANCHO_TABLERO = 10  # Número de columnas
ALTO_TABLERO = 20   # Número de filas

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (128, 128, 128)

# Definición de las formas de los tetrominós
# Cada forma es una lista de coordenadas (x, y) relativas a un punto de pivote
FORMAS_PIEZAS = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Colores para las piezas (corresponden a las formas de arriba)
COLORES_PIEZAS = [
    (0, 255, 255),   # Cian (I)
    (0, 0, 255),     # Azul (J)
    (255, 165, 0),   # Naranja (L)
    (255, 255, 0),   # Amarillo (O)
    (0, 255, 0),     # Verde (S)
    (128, 0, 128),   # Púrpura (T)
    (255, 0, 0)      # Rojo (Z)
]

class Pieza:
    def __init__(self, x, y, forma_idx):
        self.x = x
        self.y = y
        self.forma_idx = forma_idx
        self.forma = FORMAS_PIEZAS[forma_idx]
        self.color = COLORES_PIEZAS[forma_idx]
        self.rotacion = 0
        
    def rotar(self):
        # Transponer la matriz (girar 90 grados)
        filas = len(self.forma)
        columnas = len(self.forma[0])
        nueva_forma = [[0 for _ in range(filas)] for _ in range(columnas)]
        
        for i in range(filas):
            for j in range(columnas):
                nueva_forma[j][filas-1-i] = self.forma[i][j]
                
        return nueva_forma

    def dibujar(self, pantalla_juego):
        for fila_idx, fila in enumerate(self.forma):
            for col_idx, celda in enumerate(fila):
                if celda:
                    pygame.draw.rect(pantalla_juego, self.color,
                                     ( (self.x + col_idx) * TAMANO_BLOQUE, 
                                       (self.y + fila_idx) * TAMANO_BLOQUE, 
                                       TAMANO_BLOQUE, TAMANO_BLOQUE), 0)
                    pygame.draw.rect(pantalla_juego, GRIS, 
                                     ( (self.x + col_idx) * TAMANO_BLOQUE, 
                                       (self.y + fila_idx) * TAMANO_BLOQUE, 
                                       TAMANO_BLOQUE, TAMANO_BLOQUE), 1) # Borde

def crear_tablero():
    return [[NEGRO for _ in range(ANCHO_TABLERO)] for _ in range(ALTO_TABLERO)]

def hay_colision(tablero, pieza, offset_x=0, offset_y=0):
    for fila_idx, fila in enumerate(pieza.forma):
        for col_idx, celda in enumerate(fila):
            if celda:
                x = pieza.x + col_idx + offset_x
                y = pieza.y + fila_idx + offset_y
                
                # Verificar límites del tablero
                if x < 0 or x >= ANCHO_TABLERO or y >= ALTO_TABLERO:
                    return True
                # Verificar colisión con bloques fijos
                if y >= 0 and tablero[y][x] != NEGRO:
                    return True
    return False

def fijar_pieza(tablero, pieza):
    for fila_idx, fila in enumerate(pieza.forma):
        for col_idx, celda in enumerate(fila):
            if celda:
                x = pieza.x + col_idx
                y = pieza.y + fila_idx
                if y >= 0:  # Solo fijar si está dentro del tablero
                    tablero[y][x] = pieza.color
    
    # Verificar líneas completas
    lineas_completas = 0
    y = ALTO_TABLERO - 1
    while y >= 0:
        if all(celda != NEGRO for celda in tablero[y]):
            # Mover todas las filas superiores hacia abajo
            for y2 in range(y, 0, -1):
                tablero[y2] = tablero[y2-1].copy()
            tablero[0] = [NEGRO] * ANCHO_TABLERO
            lineas_completas += 1
        else:
            y -= 1
    return lineas_completas

def dibujar_tablero(pantalla_juego, tablero_logica):
    # Dibuja los bloques fijados en el tablero
    for y, fila in enumerate(tablero_logica):
        for x, color_celda in enumerate(fila):
            if color_celda != NEGRO: # Si la celda no está vacía
                pygame.draw.rect(pantalla_juego, color_celda,
                                 (x * TAMANO_BLOQUE, y * TAMANO_BLOQUE, 
                                  TAMANO_BLOQUE, TAMANO_BLOQUE), 0)
                pygame.draw.rect(pantalla_juego, GRIS, 
                                 (x * TAMANO_BLOQUE, y * TAMANO_BLOQUE, 
                                  TAMANO_BLOQUE, TAMANO_BLOQUE), 1) # Borde

    # Dibuja las líneas de la cuadrícula del tablero
    for x in range(ANCHO_TABLERO + 1):
        pygame.draw.line(pantalla_juego, GRIS, (x * TAMANO_BLOQUE, 0), (x * TAMANO_BLOQUE, ALTO_PANTALLA))
    for y in range(ALTO_TABLERO + 1):
        pygame.draw.line(pantalla_juego, GRIS, (0, y * TAMANO_BLOQUE), (ANCHO_PANTALLA, y * TAMANO_BLOQUE))

def nueva_pieza():
    # Elige una forma de pieza al azar
    idx_forma = random.randint(0, len(FORMAS_PIEZAS) - 1)
    # Crea una nueva pieza en la parte superior central del tablero
    # La posición x se calcula para centrar la pieza (aproximadamente)
    # La forma más ancha es la 'I' con 4 bloques, las demás son de 2 o 3.
    # Para simplificar, empezamos en x=ANCHO_TABLERO // 2 - 2 (para la I)
    # o ANCHO_TABLERO // 2 - 1 (para otras)
    # Por ahora, un valor fijo que funcione para la mayoría:
    nueva_x = ANCHO_TABLERO // 2 - 1 
    if idx_forma == 0: # Si es la pieza 'I'
        nueva_x = ANCHO_TABLERO // 2 - 2
    return Pieza(nueva_x, 0, idx_forma) # y=0 es la fila superior

# Configuración de la pantalla
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Tetris")

# Reloj para controlar los FPS
reloj = pygame.time.Clock()

# Inicializar el tablero
tablero_juego = crear_tablero()

# Crear la primera pieza
pieza_actual = nueva_pieza()

# Control del tiempo para la caída de la pieza
tiempo_caida = 0
intervalo_caida = 750 # milisegundos (0.75 segundos)

# Bucle principal del juego
ejecutando = True
while ejecutando:
    # Manejo de eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
            
        if evento.type == pygame.KEYDOWN:
            if not pieza_actual:
                continue
                
            if evento.key == pygame.K_LEFT:
                if not hay_colision(tablero_juego, pieza_actual, offset_x=-1):
                    pieza_actual.x -= 1
                    
            elif evento.key == pygame.K_RIGHT:
                if not hay_colision(tablero_juego, pieza_actual, offset_x=1):
                    pieza_actual.x += 1
                    
            elif evento.key == pygame.K_DOWN:
                if not hay_colision(tablero_juego, pieza_actual, offset_y=1):
                    pieza_actual.y += 1
                    
            elif evento.key == pygame.K_UP or evento.key == pygame.K_SPACE:
                # Rotar la pieza
                forma_original = pieza_actual.forma
                pieza_actual.forma = pieza_actual.rotar()
                if hay_colision(tablero_juego, pieza_actual):
                    pieza_actual.forma = forma_original  # Deshacer la rotación si hay colisión
                    
            elif evento.key == pygame.K_SPACE:
                # Caída rápida
                while not hay_colision(tablero_juego, pieza_actual, offset_y=1):
                    pieza_actual.y += 1
                fijar_pieza(tablero_juego, pieza_actual)
                pieza_actual = nueva_pieza()
                if hay_colision(tablero_juego, pieza_actual):
                    print("¡Juego terminado!")
                    ejecutando = False

    # Caída automática de la pieza
    tiempo_actual = pygame.time.get_ticks()
    if tiempo_actual - tiempo_caida > intervalo_caida and pieza_actual:
        if not hay_colision(tablero_juego, pieza_actual, offset_y=1):
            pieza_actual.y += 1
        else:
            fijar_pieza(tablero_juego, pieza_actual)
            pieza_actual = nueva_pieza()
            if hay_colision(tablero_juego, pieza_actual):
                print("¡Juego terminado!")
                ejecutando = False
        tiempo_caida = tiempo_actual


    # Dibujar en la pantalla
    pantalla.fill(NEGRO)
    dibujar_tablero(pantalla, tablero_juego)
    if pieza_actual:
        pieza_actual.dibujar(pantalla)

    pygame.display.flip()
    reloj.tick(30) # 30 FPS

pygame.quit()
sys.exit()
