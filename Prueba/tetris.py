"""
========================================
TETRIS GAME - PYGAME IMPLEMENTATION
========================================

This file implements a complete Tetris game using the Pygame library.
The game features:
- Classic tetromino pieces (I, J, L, O, S, T, Z shapes)
- Piece rotation and movement controls
- Line clearing mechanics
- Collision detection system
- Automatic piece falling with timer
- Game over detection

Controls:
- Left/Right Arrow: Move piece horizontally
- Down Arrow: Fast drop
- Up Arrow/Space: Rotate piece
- Space: Hard drop (instant fall to bottom)

Author: Game Implementation
Purpose: Provide classic Tetris gameplay as part of arcade game collection
"""

# ========================================
# IMPORT STATEMENTS
# ========================================

import pygame      # Main game engine for graphics, input, and timing
import sys         # System operations for clean exit
import random      # Random number generation for piece selection

# ========================================
# PYGAME INITIALIZATION
# ========================================

# Initialize all Pygame modules (graphics, sound, input systems)
pygame.init()

# ========================================
# GAME CONFIGURATION CONSTANTS
# ========================================

# Screen dimensions in pixels
ANCHO_PANTALLA = 300    # Screen width (10 columns × 30 pixels per block)
ALTO_PANTALLA = 600     # Screen height (20 rows × 30 pixels per block)
TAMANO_BLOQUE = 30      # Size of each tetromino block in pixels

# Game board dimensions in grid units
ANCHO_TABLERO = 10      # Number of columns in the game board
ALTO_TABLERO = 20       # Number of rows in the game board

# ========================================
# COLOR DEFINITIONS
# ========================================

# Basic colors for UI elements
NEGRO = (0, 0, 0)        # Black - background and empty cells
BLANCO = (255, 255, 255) # White - unused but available for UI text
GRIS = (128, 128, 128)   # Gray - grid lines and block borders

# ========================================
# TETROMINO PIECE DEFINITIONS
# ========================================

# Definition of tetromino shapes using 2D arrays
# Each shape is represented as a matrix where 1 = filled block, 0 = empty space
# These are the classic 7 tetromino pieces used in Tetris
FORMAS_PIEZAS = [
    [[1, 1, 1, 1]],                    # I-piece: straight line (4 blocks)
    [[1, 0, 0], [1, 1, 1]],           # J-piece: reverse L shape
    [[0, 0, 1], [1, 1, 1]],           # L-piece: standard L shape
    [[1, 1], [1, 1]],                 # O-piece: square (2x2 blocks)
    [[0, 1, 1], [1, 1, 0]],           # S-piece: zigzag shape
    [[0, 1, 0], [1, 1, 1]],           # T-piece: T shape
    [[1, 1, 0], [0, 1, 1]]            # Z-piece: reverse zigzag
]

# Color assignments for each tetromino piece type
# Colors follow classic Tetris color scheme conventions
COLORES_PIEZAS = [
    (0, 255, 255),   # Cyan - I piece (bright blue-green)
    (0, 0, 255),     # Blue - J piece (classic blue)
    (255, 165, 0),   # Orange - L piece (bright orange)
    (255, 255, 0),   # Yellow - O piece (bright yellow)
    (0, 255, 0),     # Green - S piece (bright green)
    (128, 0, 128),   # Purple - T piece (magenta/purple)
    (255, 0, 0)      # Red - Z piece (bright red)
]

# ========================================
# TETROMINO PIECE CLASS
# ========================================

class Pieza:
    """
    Represents a single tetromino piece in the game.
    
    This class handles:
    - Piece position and movement
    - Rotation mechanics
    - Visual rendering
    - Shape and color management
    """
    
    def __init__(self, x, y, forma_idx):
        """
        Initialize a new tetromino piece.
        
        Args:
            x (int): Starting x-coordinate on the game board
            y (int): Starting y-coordinate on the game board  
            forma_idx (int): Index into FORMAS_PIEZAS array to determine piece type
        """
        self.x = x                              # Current x position on board grid
        self.y = y                              # Current y position on board grid
        self.forma_idx = forma_idx              # Index to identify piece type
        self.forma = FORMAS_PIEZAS[forma_idx]   # 2D array representing piece shape
        self.color = COLORES_PIEZAS[forma_idx]  # RGB color tuple for this piece
        self.rotacion = 0                       # Current rotation state (0-3)
        
    def rotar(self):
        """
        Rotate the piece 90 degrees clockwise.
        
        Uses matrix transposition algorithm:
        1. Transpose the matrix (swap rows and columns)
        2. Reverse each row to complete the 90-degree rotation
        
        Returns:
            list: New 2D array representing the rotated piece shape
        """
        # Get dimensions of current piece shape
        filas = len(self.forma)         # Number of rows in current shape
        columnas = len(self.forma[0])   # Number of columns in current shape
        
        # Create new matrix with swapped dimensions (transpose preparation)
        nueva_forma = [[0 for _ in range(filas)] for _ in range(columnas)]
        
        # Apply rotation transformation: nueva_forma[j][filas-1-i] = forma[i][j]
        # This performs transpose + horizontal flip = 90-degree clockwise rotation
        for i in range(filas):
            for j in range(columnas):
                nueva_forma[j][filas-1-i] = self.forma[i][j]
                
        return nueva_forma

    def dibujar(self, pantalla_juego):
        """
        Render the piece on the game screen.
        
        Draws each filled block of the piece with:
        - Filled rectangle in the piece's color
        - Gray border around each block for visual separation
        
        Args:
            pantalla_juego: Pygame surface to draw on
        """
        # Iterate through each cell in the piece's shape matrix
        for fila_idx, fila in enumerate(self.forma):
            for col_idx, celda in enumerate(fila):
                if celda:  # Only draw filled blocks (value = 1)
                    # Calculate pixel coordinates from grid coordinates
                    x_pixel = (self.x + col_idx) * TAMANO_BLOQUE
                    y_pixel = (self.y + fila_idx) * TAMANO_BLOQUE
                    
                    # Draw filled rectangle for the block
                    pygame.draw.rect(pantalla_juego, self.color,
                                   (x_pixel, y_pixel, TAMANO_BLOQUE, TAMANO_BLOQUE), 0)
                    
                    # Draw border around the block for visual definition
                    pygame.draw.rect(pantalla_juego, GRIS, 
                                   (x_pixel, y_pixel, TAMANO_BLOQUE, TAMANO_BLOQUE), 1)

# ========================================
# GAME BOARD MANAGEMENT FUNCTIONS
# ========================================

def crear_tablero():
    """
    Create and initialize the game board.
    
    Creates a 2D array representing the game board where:
    - Each cell contains a color tuple (initially all black/empty)
    - Dimensions are ALTO_TABLERO × ANCHO_TABLERO
    - Black color indicates empty cell
    - Other colors indicate fixed/placed pieces
    
    Returns:
        list: 2D array representing empty game board
    """
    return [[NEGRO for _ in range(ANCHO_TABLERO)] for _ in range(ALTO_TABLERO)]

def hay_colision(tablero, pieza, offset_x=0, offset_y=0):
    """
    Check if a piece would collide with boundaries or existing blocks.
    
    Tests collision detection by checking if the piece (with optional offset)
    would overlap with:
    - Game board boundaries (left, right, bottom walls)
    - Already placed pieces on the board
    
    Args:
        tablero (list): 2D array representing the game board
        pieza (Pieza): The piece to test for collision
        offset_x (int): Horizontal offset to test (for movement preview)
        offset_y (int): Vertical offset to test (for movement preview)
    
    Returns:
        bool: True if collision detected, False if position is valid
    """
    # Check each filled block in the piece's current shape
    for fila_idx, fila in enumerate(pieza.forma):
        for col_idx, celda in enumerate(fila):
            if celda:  # Only check filled blocks
                # Calculate the absolute position with offsets
                x = pieza.x + col_idx + offset_x
                y = pieza.y + fila_idx + offset_y
                
                # Check boundary collisions
                if x < 0 or x >= ANCHO_TABLERO or y >= ALTO_TABLERO:
                    return True
                    
                # Check collision with existing placed pieces
                # Only check if y >= 0 to avoid checking above the visible board
                if y >= 0 and tablero[y][x] != NEGRO:
                    return True
    return False

def fijar_pieza(tablero, pieza):
    """
    Place a piece permanently on the game board and handle line clearing.
    
    This function:
    1. Adds the piece's blocks to the board at their current position
    2. Checks for completed horizontal lines
    3. Removes completed lines and shifts remaining blocks down
    4. Returns the number of lines cleared for scoring
    
    Args:
        tablero (list): 2D array representing the game board
        pieza (Pieza): The piece to place permanently
    
    Returns:
        int: Number of lines cleared (0-4, typically 0-1 for most clears)
    """
    # ========================================
    # PLACE PIECE BLOCKS ON BOARD
    # ========================================
    
    # Add each filled block of the piece to the board
    for fila_idx, fila in enumerate(pieza.forma):
        for col_idx, celda in enumerate(fila):
            if celda:  # Only process filled blocks
                x = pieza.x + col_idx
                y = pieza.y + fila_idx
                # Only place blocks that are within the visible board area
                if y >= 0:
                    tablero[y][x] = pieza.color
    
    # ========================================
    # LINE CLEARING ALGORITHM
    # ========================================
    
    # Track number of lines cleared for scoring/statistics
    lineas_completas = 0
    
    # Start from bottom and work upward to handle multiple line clears
    y = ALTO_TABLERO - 1
    while y >= 0:
        # Check if current row is completely filled
        if all(celda != NEGRO for celda in tablero[y]):
            # ========================================
            # CLEAR COMPLETED LINE
            # ========================================
            
            # Move all rows above the cleared line down by one position
            for y2 in range(y, 0, -1):
                tablero[y2] = tablero[y2-1].copy()  # Copy row above into current row
            
            # Fill the top row with empty blocks
            tablero[0] = [NEGRO] * ANCHO_TABLERO
            
            # Increment counter for cleared lines
            lineas_completas += 1
            
            # Don't increment y since we need to check this row again
            # (it now contains the row that was previously above it)
        else:
            # Row is not complete, move to next row up
            y -= 1
            
    return lineas_completas

# ========================================
# RENDERING AND DRAWING FUNCTIONS
# ========================================

def dibujar_tablero(pantalla_juego, tablero_logica):
    """
    Render the game board and grid lines on the screen.
    
    This function draws:
    1. All placed/fixed pieces on the board with their colors
    2. Grid lines to show the game board structure
    3. Borders around each placed block for visual clarity
    
    Args:
        pantalla_juego: Pygame surface to draw on
        tablero_logica (list): 2D array containing board state and piece colors
    """
    # ========================================
    # DRAW PLACED PIECES
    # ========================================
    
    # Render all non-empty blocks that have been placed on the board
    for y, fila in enumerate(tablero_logica):
        for x, color_celda in enumerate(fila):
            if color_celda != NEGRO:  # Skip empty cells
                # Draw filled rectangle for the placed block
                pygame.draw.rect(pantalla_juego, color_celda,
                               (x * TAMANO_BLOQUE, y * TAMANO_BLOQUE, 
                                TAMANO_BLOQUE, TAMANO_BLOQUE), 0)
                
                # Draw border around the block for visual definition
                pygame.draw.rect(pantalla_juego, GRIS, 
                               (x * TAMANO_BLOQUE, y * TAMANO_BLOQUE, 
                                TAMANO_BLOQUE, TAMANO_BLOQUE), 1)

    # ========================================
    # DRAW GAME BOARD GRID
    # ========================================
    
    # Draw vertical grid lines (column separators)
    for x in range(ANCHO_TABLERO + 1):
        x_pixel = x * TAMANO_BLOQUE
        pygame.draw.line(pantalla_juego, GRIS, 
                        (x_pixel, 0), (x_pixel, ALTO_PANTALLA))
    
    # Draw horizontal grid lines (row separators)  
    for y in range(ALTO_TABLERO + 1):
        y_pixel = y * TAMANO_BLOQUE
        pygame.draw.line(pantalla_juego, GRIS, 
                        (0, y_pixel), (ANCHO_PANTALLA, y_pixel))

# ========================================
# PIECE GENERATION SYSTEM
# ========================================

def nueva_pieza():
    """
    Generate a new random tetromino piece at the top of the board.
    
    This function:
    1. Randomly selects one of the 7 tetromino types
    2. Calculates appropriate starting position (horizontally centered)
    3. Creates and returns a new Pieza instance
    
    The starting position is calculated to center most pieces:
    - I-piece (4 blocks wide): starts at x = ANCHO_TABLERO // 2 - 2
    - Other pieces (2-3 blocks wide): start at x = ANCHO_TABLERO // 2 - 1
    
    Returns:
        Pieza: New tetromino piece ready to be controlled by player
    """
    # Randomly select a piece type from available shapes
    idx_forma = random.randint(0, len(FORMAS_PIEZAS) - 1)
    
    # Calculate starting x position to center the piece horizontally
    # Default position works for most pieces (2-3 blocks wide)
    nueva_x = ANCHO_TABLERO // 2 - 1 
    
    # Special case for I-piece which is 4 blocks wide
    if idx_forma == 0:  # I-piece index
        nueva_x = ANCHO_TABLERO // 2 - 2
    
    # Create new piece at top of board (y=0) with calculated x position
    return Pieza(nueva_x, 0, idx_forma)

# ========================================
# GAME INITIALIZATION
# ========================================

# Create the main game window
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Tetris")  # Set window title

# Initialize game timing control
reloj = pygame.time.Clock()  # Controls frame rate and timing

# ========================================
# GAME STATE INITIALIZATION  
# ========================================

# Create empty game board (2D array filled with black/empty cells)
tablero_juego = crear_tablero()

# Generate the first tetromino piece for the player to control
pieza_actual = nueva_pieza()

# ========================================
# AUTOMATIC PIECE FALLING SYSTEM
# ========================================

# Timing variables for automatic piece descent
tiempo_caida = 0          # Timestamp of last automatic fall
intervalo_caida = 750     # Time between automatic falls (milliseconds = 0.75 seconds)

# ========================================
# MAIN GAME LOOP
# ========================================

# Primary game execution loop - continues until player quits
ejecutando = True
while ejecutando:
    
    # ========================================
    # EVENT HANDLING SYSTEM
    # ========================================
    
    # Process all pending input events (keyboard, mouse, window)
    for evento in pygame.event.get():
        
        # Handle window close button or ALT+F4
        if evento.type == pygame.QUIT:
            ejecutando = False
            
        # Handle keyboard input for piece control
        if evento.type == pygame.KEYDOWN:
            # Skip input processing if no active piece
            if not pieza_actual:
                continue
                
            # ========================================
            # HORIZONTAL MOVEMENT CONTROLS
            # ========================================
            
            # LEFT ARROW: Move piece left
            if evento.key == pygame.K_LEFT:
                # Only move if no collision detected
                if not hay_colision(tablero_juego, pieza_actual, offset_x=-1):
                    pieza_actual.x -= 1
                    
            # RIGHT ARROW: Move piece right  
            elif evento.key == pygame.K_RIGHT:
                # Only move if no collision detected
                if not hay_colision(tablero_juego, pieza_actual, offset_x=1):
                    pieza_actual.x += 1
            
            # ========================================
            # VERTICAL MOVEMENT CONTROLS
            # ========================================
                    
            # DOWN ARROW: Soft drop (faster descent)
            elif evento.key == pygame.K_DOWN:
                # Only move if no collision detected
                if not hay_colision(tablero_juego, pieza_actual, offset_y=1):
                    pieza_actual.y += 1
            
            # ========================================
            # ROTATION CONTROLS
            # ========================================
                    
            # UP ARROW or SPACE: Rotate piece clockwise
            elif evento.key == pygame.K_UP or evento.key == pygame.K_SPACE:
                # Store original shape in case rotation fails
                forma_original = pieza_actual.forma
                
                # Attempt rotation
                pieza_actual.forma = pieza_actual.rotar()
                
                # Check if rotated position causes collision
                if hay_colision(tablero_juego, pieza_actual):
                    # Rotation invalid - revert to original shape
                    pieza_actual.forma = forma_original
            
            # ========================================  
            # HARD DROP CONTROL
            # ========================================
                    
            # SPACE: Hard drop (instant fall to bottom)
            elif evento.key == pygame.K_SPACE:
                # Move piece down until it hits something
                while not hay_colision(tablero_juego, pieza_actual, offset_y=1):
                    pieza_actual.y += 1
                
                # Place piece permanently and generate new one
                fijar_pieza(tablero_juego, pieza_actual)
                pieza_actual = nueva_pieza()
                
                # Check for game over (new piece spawns in occupied space)
                if hay_colision(tablero_juego, pieza_actual):
                    print("¡Juego terminado!")
                    ejecutando = False    # ========================================
    # AUTOMATIC PIECE FALLING LOGIC
    # ========================================
    
    # Handle automatic downward movement of pieces based on time
    tiempo_actual = pygame.time.get_ticks()  # Get current time in milliseconds
    
    # Check if enough time has passed for automatic fall
    if tiempo_actual - tiempo_caida > intervalo_caida and pieza_actual:
        
        # Try to move piece down one row
        if not hay_colision(tablero_juego, pieza_actual, offset_y=1):
            # No collision - piece can fall normally
            pieza_actual.y += 1
        else:
            # Collision detected - piece has landed
            
            # Place current piece permanently on the board
            fijar_pieza(tablero_juego, pieza_actual)
            
            # Generate new piece for player to control
            pieza_actual = nueva_pieza()
            
            # Check for game over condition
            if hay_colision(tablero_juego, pieza_actual):
                print("¡Juego terminado!")
                ejecutando = False
                
        # Update timing for next automatic fall
        tiempo_caida = tiempo_actual

    # ========================================
    # RENDERING SYSTEM
    # ========================================

    # Clear screen with black background
    pantalla.fill(NEGRO)
    
    # Draw the game board with all placed pieces and grid lines
    dibujar_tablero(pantalla, tablero_juego)
    
    # Draw the currently active/falling piece
    if pieza_actual:
        pieza_actual.dibujar(pantalla)

    # Update the display with all drawn elements
    pygame.display.flip()
    
    # Control frame rate to 30 FPS for smooth gameplay
    reloj.tick(30)

# ========================================
# GAME CLEANUP AND EXIT
# ========================================

# Properly shut down Pygame systems
pygame.quit()

# Exit the Python program cleanly
sys.exit()
