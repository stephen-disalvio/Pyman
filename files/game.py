import os, sys, pygame, constants, time

from pygame.locals import *

# from Start import Start
from Menus import Start, Retry
from Sprites import Tile, Ghost, Pacman, Pellet, Power_Pellet

# Initialize Pygame
pygame.init()

# Initialize Clock
mainClock = pygame.time.Clock()

# Initialize the game's Start Menu
Start()

# Constants
LIVES = 3
POINTS = 0

# text
font_system = pygame.font.Font("../font/joystix.ttf", 14)
text = font_system.render("POINTS: {}".format(POINTS), True, constants.WHITE)

# Initialize window
window = pygame.display.set_mode((constants.WINDOWWIDTH, constants.WINDOWHEIGHT), 0, 32)

# Set background
background = pygame.image.load('../sprites/pacman-level.png')
window.blit(background, (0, 0))

# Pixels per loop
MOVESPEED = 4

# Create Tilees for collisions
walls = pygame.sprite.Group()

# Grid (for movement)
# Uses Tile objects
tile_system = pygame.sprite.Group()

# Pellets
# To create a Pellet object: Pellet(x, y)
pellets = pygame.sprite.Group()

# Magic Pellets
power_pellets = pygame.sprite.Group()

# Teleporters
l_transporter = pygame.sprite.GroupSingle(Tile(0, 16 * 15))
r_transporter = pygame.sprite.GroupSingle(Tile(16 * 27, 16 * 15))

# Respawner
respawner_tile = Tile(208, 192)
respawner = pygame.sprite.GroupSingle(respawner_tile)

# Create Grid System
x = 0
y = 16
while y < constants.WINDOWHEIGHT:
    while x < constants.WINDOWWIDTH:
        # 16x16 area used for cropping
        selected_area = pygame.Rect(x, y, 16, 16)
        
        # Creates a cropped image from the background
        cropped_image = background.subsurface(selected_area)
        
        # If the cropped image's color is BLACK
        if pygame.transform.average_color(cropped_image)[:3] == constants.BLACK:
            # Create grid for movement
            grid_member = Tile(x, y)
            grid_member.check_possible_moves(x, y)
            tile_system.add(grid_member)
        else:
            walls.add(Tile(x, y))
        
        x += 16
    y += 16
    x = 0
    
# Initialize Pacman
pacman = Pacman(224, 384, MOVESPEED) # 16 * 14, 16 * 24
pacman_group = pygame.sprite.GroupSingle(pacman)
    
# Initialize Ghosts
ghost = Ghost(208, 192, MOVESPEED)
ghost_group = pygame.sprite.Group(ghost)
    
# Initialize movement variable
movement = 'R'
last_movement = 'R'

# Initialize timer
time_start = None
time_end = None

def create_pellets():
    # Goes through the entire map and outlines which 16x16 areas are black
    # This identifies where Pacman and Pellets can and cannot go
    list = [3, 4, 8, 9, 10, 17, 18, 19, 23, 24]
    columns = [i * constants.SPRITEWIDTH for i in list]
    x = 0
    y = 16
    while y < constants.WINDOWHEIGHT:
        while x < constants.WINDOWWIDTH:
            # 16x16 area used for cropping
            selected_area = pygame.Rect(x, y, 16, 16)
            
            # Creates a cropped image from the background
            cropped_image = background.subsurface(selected_area)
            
            # If the cropped image's color is BLACK
            if pygame.transform.average_color(cropped_image)[:3] == constants.BLACK:                
                # These if-statements are for specific cases
                if y == constants.SPRITEHEIGHT*4:
                    if not x in columns:
                        pellets.add(Pellet(selected_area.centerx, selected_area.centery))
                elif not (y >= constants.SPRITEHEIGHT*10 and y <= constants.SPRITEHEIGHT*20):
                    pellets.add(Pellet(selected_area.centerx, selected_area.centery))
                else:
                    if x == constants.SPRITEWIDTH*6 or x == constants.SPRITEWIDTH*21:
                        pellets.add(Pellet(selected_area.centerx, selected_area.centery))
            
            x += 16
        y += 16
        x = 0


def load_game():
    """Loads map and pellets"""    
    # Creates the map
    window.blit(background, (0, 0))
    
    # Sets Pacman to its default position
    pacman.reset_pos()
    
    # Create the pellets
    pellets.empty()
    create_pellets()
    
    # Create the magic pellets
    power_pellets.empty()
    coordinates = [(16*1, 16*4), (16*26, 16*4), (16*1, 16*24), (16*26, 16*24)]
    for (x, y) in coordinates:
        selected_area = pygame.Rect(x, y, 16, 16)
        power_pellets.add(Power_Pellet(selected_area.centerx, selected_area.centery))
    
    # Draw all sprites
    pellets.draw(window)
    power_pellets.draw(window)
    pacman_group.draw(window)
    ghost_group.draw(window)
    
    # "Ready" Message
    text = font_system.render("READY!".format(POINTS), True, constants.YELLOW)
    window.blit(text, (192, 288))
    pygame.display.update()
    time.sleep(2.5)

    
def continue_game():
    """Loads sprites and leaves pellets the same"""
    # Creates the map
    window.blit(background, (0, 0))
    
    # Sets Pacman & Ghost to their default position
    pacman.reset_pos()
    ghost.reset_pos()
    
    # Updates Pacman's movement
    pacman_current_grid = pygame.sprite.spritecollide(pacman, tile_system, False)
    p_grid = pacman_current_grid.pop()
    
    # Updates Ghost's movement
    ghost_current_grid = pygame.sprite.spritecollide(ghost, tile_system, False)
    g_grid = ghost_current_grid.pop()
    ghost.create_path(p_grid, [g_grid], tile_system.copy())
    
    # Draw all sprites
    pellets.draw(window)
    pacman_group.draw(window)
    ghost_group.draw(window)
    
    # "Ready" Message
    text = font_system.render("READY!".format(POINTS), True, constants.YELLOW)
    window.blit(text, (192, 288))
    pygame.display.update()
    time.sleep(2.5)
    
    
def update_window():
    """Updates the window by redrawing the background and sprites"""

    # Redraw the background and sprites
    window.blit(background, (0, 0))
    pellets.draw(window)
    power_pellets.draw(window)
    pacman_group.draw(window)
    ghost_group.draw(window)
    
    # Redraw the text
    text = font_system.render("POINTS: {}".format(POINTS), True, constants.WHITE)
    window.blit(text, (1, 1))
    
    # Redraw the life system
    x = 16 * 20
    for _ in range(LIVES):
        sprite = pygame.image.load('../sprites/pacman-2.png')
        window.blit(sprite, (x, 0))
        x += 16
    
    # Update the display
    pygame.display.update()
    mainClock.tick(60)
    

def transport_right(sprite):
    """Transports sprite from the right side of the window to the left side"""
    
    while sprite.rect.left <= WINDOWWIDTH:
        sprite.rect.right += 10
        update_window()
        
    sprite.rect.right = 0
    
    while sprite.rect.left <= 0:
        sprite.rect.right += 10
        update_window()
        
    sprite.rect = pygame.Rect(16 * 1, 16 * 15, 16, 16)
    
    
def transport_left(sprite):
    """Transports sprite from the left side of the window to the right side"""
    
    while sprite.rect.right >= 0:
        sprite.rect.left -= 10
        update_window()
        
    sprite.rect.left = constants.WINDOWWIDTH
    
    while sprite.rect.right >= constants.WINDOWWIDTH:
        sprite.rect.left -= 10
        update_window()
        
    sprite.rect = pygame.Rect(16 * 26, 16 * 15, 16, 16)
    
    
def test_movement(move, speed, pacman):
    test = Tile(pacman.rect.x, pacman.rect.y)
    global last_movement
    if move == 'U':
        test.rect.top -= speed
        if not pygame.sprite.spritecollide(test, walls, False):
            last_movement = 'U'
            pacman_group.update(move)
        else:
            test_last_movement(last_movement, speed, pacman)
    elif move == 'D':
        test.rect.bottom += speed
        if not pygame.sprite.spritecollide(test, walls, False):
            last_movement = 'D'
            pacman_group.update(move)
        else:
            test_last_movement(last_movement, speed, pacman)
    elif move == 'L':
        test.rect.left -= speed
        if not pygame.sprite.spritecollide(test, walls, False):
            last_movement = 'L'
            pacman_group.update(move)
        else:
            test_last_movement(last_movement, speed, pacman)
    elif move == 'R':
        test.rect.right += speed
        if not pygame.sprite.spritecollide(test, walls, False):
            last_movement = 'R'
            pacman_group.update(move)
        else:
            test_last_movement(last_movement, speed, pacman)

            
def test_last_movement(move, speed, pacman):
    test = Tile(pacman.rect.x, pacman.rect.y)
    global last_movement
    if move == 'U':
        test.rect.top -= speed
        if not pygame.sprite.spritecollide(test, walls, False):
            pacman_group.update(move)
        else:
            pacman_group.update('')
    elif move == 'D':
        test.rect.bottom += speed
        if not pygame.sprite.spritecollide(test, walls, False):
            pacman_group.update(move)
        else:
            pacman_group.update('')
    elif move == 'L':
        test.rect.left -= speed
        if not pygame.sprite.spritecollide(test, walls, False):
            pacman_group.update(move)
        else:
            pacman_group.update('')
    elif move == 'R':
        test.rect.right += speed
        if not pygame.sprite.spritecollide(test, walls, False):
            pacman_group.update(move)
        else:
            pacman_group.update('')
    
load_game()
###############################################################################
##########                     MAIN GAME LOOP                        ##########
###############################################################################
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit() 
        if event.type == KEYDOWN:
            if event.key == K_UP:
                movement = 'U'
            if event.key == K_DOWN:
                movement = 'D'
            if event.key == K_LEFT:
                movement = 'L'
            if event.key == K_RIGHT:
                movement = 'R'
    
    time_end = time.time()
    if time_start and time_end:
        if (time_end-time_start) >= 5.0:
            if ghost.isVulnerable:
                ghost.toggleVulnerability()
                time_start = None
            elif ghost.state == 'P':
                ghost.state = 'S'
                
    if ghost.pixel == 0:
        # Updates Pacman's movement
        pacman_current_grid = pygame.sprite.spritecollide(pacman, tile_system, False)
        respawner_current_grid = pygame.sprite.spritecollide(respawner_tile, tile_system, False)
        target = None
        if ghost.state == 'A':
            target = pacman_current_grid.pop()
        else:
            target = respawner_current_grid.pop()
        # Updates Ghost's movement
        ghost_current_grid = pygame.sprite.spritecollide(ghost, tile_system, False)
        g_grid = ghost_current_grid.pop()
        
        ghost.create_path(target, [g_grid], tile_system.copy())
    
    # move the sprite(pacman)
    test_movement(movement, MOVESPEED, pacman)
    ghost_group.update(g_grid, target)
    update_window()
    
    # Check if Pacman collided with any Pellets
    # True = Pellet will be destroyed when collided with
    eaten_pellets = pygame.sprite.spritecollide(pacman, pellets, True)
    for pellet in eaten_pellets:
        POINTS += 10
        
    # Check if Pacman collided with any Magic Pellets
    # True = Magic Pellet will be destroyed when collided with
    eaten_magic_pellets = pygame.sprite.spritecollide(pacman, power_pellets, True)
    for magic_pellet in eaten_magic_pellets:
        POINTS += 10
        time_start = time.time()
        for ghost in ghost_group:
            ghost.toggleVulnerability()
        
        
    # Check if all Pellets are eaten
    if len(pellets) == 0:
        load_game()
        movement = 'R'
        last_movement = 'R'
    
    # check if Pacman collided with any Ghosts
    # If so, check if they are vulnerable
    # If true, destroy the sprite
    # If not, quit the game
    collided_ghosts = pygame.sprite.spritecollide(pacman, ghost_group, False)
    for ghost in collided_ghosts:
        if ghost.isVulnerable:
            ghost.toggleVulnerability()
            ghost.toggle_death()
            time_start = None
            POINTS += 200
        elif ghost.state == 'A':
            window.fill(constants.BLACK)
            pygame.display.update()
            LIVES -= 1
            pacman.death()
            if LIVES == 0:
                Retry()
                load_game()
                POINTS = 0
                LIVES = 3            
            else:
                continue_game()
            
            movement = 'R'
            last_movement = 'R'
    
    # Transport Pacman if Pacman collides with either transporter
    if pygame.sprite.spritecollide(pacman, l_transporter, False):
        transport_left(pacman)
    elif pygame.sprite.spritecollide(pacman, r_transporter, False):
        transport_right(pacman)
        
    if pygame.sprite.spritecollide(ghost, respawner, False):
        if ghost.state == 'D':
            ghost.state = 'R'
            time_start = time.time()

    # Update game
    update_window()
