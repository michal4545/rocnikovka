import pygame
import sys
import os
import time

pygame.init()

WIDTH, HEIGHT = 1024, 768
GAME_SURFACE = pygame.Surface((WIDTH, HEIGHT))
fullscreen = True
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Samurai")
icon = pygame.image.load('images/icon.png')
pygame.display.set_icon(icon)

game_state = "MENU" 
sound_volume = 0.7
menu_buttons = {
    "play": pygame.Rect(387, 450, 250, 60),
    "settings": pygame.Rect(387, 520, 250, 60),
    "controls": pygame.Rect(387, 590, 250, 60),
    "exit": pygame.Rect(387, 660, 250, 60)
}
settings_buttons = {
    "fullscreen_toggle": pygame.Rect(350, 350, 324, 80),
    "back": pygame.Rect(350, 480, 324, 80)
}
controls_buttons = {
    "back": pygame.Rect(387, 660, 250, 60)
}
slider_rect = pygame.Rect(350, 200, 300, 10)
dragging_slider = False

background_image = pygame.image.load("images/background.png").convert()
platforms_image = pygame.image.load("images/platforms.png").convert_alpha()
menu_background_image = pygame.image.load("images/MenuBackground.png").convert()
menu_background_image = pygame.transform.scale(menu_background_image, (WIDTH, HEIGHT))


def update_display_metrics():
    global DISPLAY_WIDTH, DISPLAY_HEIGHT, DISPLAY_SCALE, SCALED_WIDTH, SCALED_HEIGHT, DISPLAY_OFFSET_X, DISPLAY_OFFSET_Y
    DISPLAY_WIDTH, DISPLAY_HEIGHT = screen.get_size()
    DISPLAY_SCALE = min(DISPLAY_WIDTH / WIDTH, DISPLAY_HEIGHT / HEIGHT)
    SCALED_WIDTH = int(WIDTH * DISPLAY_SCALE)
    SCALED_HEIGHT = int(HEIGHT * DISPLAY_SCALE)
    DISPLAY_OFFSET_X = (DISPLAY_WIDTH - SCALED_WIDTH) // 2
    DISPLAY_OFFSET_Y = (DISPLAY_HEIGHT - SCALED_HEIGHT) // 2

update_display_metrics()

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, False, color)
    text_rect = text_obj.get_rect(center=(x, y))
    surface.blit(text_obj, text_rect)

def draw_button(surface, rect, text, font, is_hovered=False):
    if is_hovered:
        scaled_rect = pygame.Rect(0, 0, int(rect.width * 1.2), int(rect.height * 1.2))
        scaled_rect.center = rect.center
        pygame.draw.rect(surface, (0, 0, 0), scaled_rect, border_radius=15)
        draw_text(text, font, (255, 255, 255), surface, rect.centerx, rect.centery)
    else:
        temp_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(temp_surf, (0, 0, 0, 128), temp_surf.get_rect(), border_radius=15)
        surface.blit(temp_surf, rect.topleft)
        draw_text(text, font, (255, 255, 255), surface, rect.centerx, rect.centery)


def background(surface, camera_y):
    bg_width, bg_height = background_image.get_size()
    if bg_width <= 0 or bg_height <= 0:
        surface.fill((0, 0, 0))
        return

    first_tile_top_world_y = WORLD_HEIGHT - bg_height
    while first_tile_top_world_y > camera_y:
        first_tile_top_world_y -= bg_height

    start_y = int(first_tile_top_world_y - camera_y)
    for y in range(start_y, HEIGHT, bg_height):
        for x in range(0, WIDTH, bg_width):
            surface.blit(background_image, (x, y))

def draw_platforms(surface, camera_y):
    overlay_width, overlay_height = platforms_image.get_size()
    if overlay_width <= 0 or overlay_height <= 0:
        return

    first_tile_top_world_y = WORLD_HEIGHT - overlay_height
    while first_tile_top_world_y > camera_y:
        first_tile_top_world_y -= overlay_height

    start_y = int(first_tile_top_world_y - camera_y)
    for y in range(start_y, HEIGHT, overlay_height):
        for x in range(0, WIDTH, overlay_width):
            surface.blit(platforms_image, (x, y))

def draw_menu(screen, game_surface):
    game_surface.blit(menu_background_image, (0, 0))
    font_large = pygame.font.Font('Electroharmonix.otf', 80)
    font_button = pygame.font.Font('Electroharmonix.otf', 40)
    
    draw_text("SAMURAI", font_large, (255, 200, 100), game_surface, WIDTH // 2, 100)
    
    mouse_pos = pygame.mouse.get_pos()
    mouse_game_pos = (
        (mouse_pos[0] - DISPLAY_OFFSET_X) / DISPLAY_SCALE,
        (mouse_pos[1] - DISPLAY_OFFSET_Y) / DISPLAY_SCALE
    )
    
    play_hovered = menu_buttons["play"].collidepoint(mouse_game_pos)
    settings_hovered = menu_buttons["settings"].collidepoint(mouse_game_pos)
    controls_hovered = menu_buttons["controls"].collidepoint(mouse_game_pos)
    exit_hovered = menu_buttons["exit"].collidepoint(mouse_game_pos)
    
    draw_button(game_surface, menu_buttons["play"], "PLAY", font_button, play_hovered)
    draw_button(game_surface, menu_buttons["settings"], "SETTINGS", font_button, settings_hovered)
    draw_button(game_surface, menu_buttons["controls"], "CONTROLS", font_button, controls_hovered)
    draw_button(game_surface, menu_buttons["exit"], "EXIT", font_button, exit_hovered)
    
    scaled_surface = pygame.transform.scale(game_surface, (SCALED_WIDTH, SCALED_HEIGHT))
    screen.fill((0, 0, 0))
    screen.blit(scaled_surface, (DISPLAY_OFFSET_X, DISPLAY_OFFSET_Y))
    pygame.display.flip()
    
    return play_hovered, settings_hovered, controls_hovered, exit_hovered


def draw_controls(screen, game_surface):
    game_surface.blit(menu_background_image, (0, 0))
    font_large = pygame.font.Font('Electroharmonix.otf', 60)
    font_text = pygame.font.SysFont('MS Gothic', 28)
    font_button = pygame.font.Font('Electroharmonix.otf', 40)

    draw_text("CONTROLS", font_large, (255, 200, 100), game_surface, WIDTH // 2, 90)

    controls_lines = [
        "MOVE LEFT/RIGHT: A / D",
        "",
        "JUMP (HOLD TO CHARGE): SPACE",
        "",
        "WALL JUMP: HOLD SPACE WHILE FLYING UP BEFORE TOUCHING A WALL",
        "THEN RELEASE TO JUMP OFF THE WALL",
        "",
        "SLIDE: C",
        "",
        "TOGGLE FULLSCREEN: F11",
        "OPEN MENU: ESC"
    ]

    start_y = 200
    line_spacing = 30
    for i, line in enumerate(controls_lines):
        draw_text(line, font_text, (255, 255, 255), game_surface, WIDTH // 2, start_y + i * line_spacing)

    mouse_pos = pygame.mouse.get_pos()
    mouse_game_pos = (
        (mouse_pos[0] - DISPLAY_OFFSET_X) / DISPLAY_SCALE,
        (mouse_pos[1] - DISPLAY_OFFSET_Y) / DISPLAY_SCALE
    )

    back_hovered = controls_buttons["back"].collidepoint(mouse_game_pos)
    draw_button(game_surface, controls_buttons["back"], "BACK", font_button, back_hovered)

    scaled_surface = pygame.transform.scale(game_surface, (SCALED_WIDTH, SCALED_HEIGHT))
    screen.fill((0, 0, 0))
    screen.blit(scaled_surface, (DISPLAY_OFFSET_X, DISPLAY_OFFSET_Y))
    pygame.display.flip()

    return back_hovered

def draw_settings(screen, game_surface):
    game_surface.blit(menu_background_image, (0, 0))
    font_large = pygame.font.Font('Electroharmonix.otf', 60)
    font_button = pygame.font.Font('Electroharmonix.otf', 35)
    
    draw_text("SETTINGS", font_large, (255, 200, 100), game_surface, WIDTH // 2, 80)
    
    mouse_pos = pygame.mouse.get_pos()
    mouse_game_pos = (
        (mouse_pos[0] - DISPLAY_OFFSET_X) / DISPLAY_SCALE,
        (mouse_pos[1] - DISPLAY_OFFSET_Y) / DISPLAY_SCALE
    )
    
    draw_text(f"VOLUME: {int(sound_volume * 100)}%", font_button, (255, 255, 255), game_surface, WIDTH // 2, 150)
    
    knob_x = slider_rect.left + sound_volume * slider_rect.width
    knob_rect = pygame.Rect(knob_x - 10, slider_rect.centery - 10, 20, 20)
    pygame.draw.rect(game_surface, (100, 100, 100), slider_rect, border_radius=5)
    pygame.draw.circle(game_surface, (200, 200, 200), knob_rect.center, 10)
    
    fullscreen_text = "FULLSCREEN: ON" if fullscreen else "FULLSCREEN: OFF"
    fullscreen_hovered = settings_buttons["fullscreen_toggle"].collidepoint(mouse_game_pos)
    draw_button(game_surface, settings_buttons["fullscreen_toggle"], fullscreen_text, font_button, fullscreen_hovered)
    
    back_hovered = settings_buttons["back"].collidepoint(mouse_game_pos)
    draw_button(game_surface, settings_buttons["back"], "BACK", font_button, back_hovered)
    
    scaled_surface = pygame.transform.scale(game_surface, (SCALED_WIDTH, SCALED_HEIGHT))
    screen.fill((0, 0, 0))
    screen.blit(scaled_surface, (DISPLAY_OFFSET_X, DISPLAY_OFFSET_Y))
    pygame.display.flip()
    
    return fullscreen_hovered, back_hovered

def handle_menu_events(play_hovered, settings_hovered, controls_hovered, exit_hovered):
    global fullscreen, screen
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "QUIT"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_hovered:
                return "GAME"
            elif settings_hovered:
                return "SETTINGS"
            elif controls_hovered:
                return "CONTROLS"
            elif exit_hovered:
                return "QUIT"
    
    return "MENU"

def handle_settings_events(fullscreen_hovered, back_hovered):
    global fullscreen, screen, sound_volume, dragging_slider
    
    mouse_pos = pygame.mouse.get_pos()
    mouse_game_pos = (
        (mouse_pos[0] - DISPLAY_OFFSET_X) / DISPLAY_SCALE,
        (mouse_pos[1] - DISPLAY_OFFSET_Y) / DISPLAY_SCALE
    )
    
    knob_x = slider_rect.left + sound_volume * slider_rect.width
    knob_rect = pygame.Rect(knob_x - 10, slider_rect.centery - 10, 20, 20)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "QUIT"
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "MENU"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if knob_rect.collidepoint(mouse_game_pos) or slider_rect.collidepoint(mouse_game_pos):
                dragging_slider = True
                rel_x = mouse_game_pos[0] - slider_rect.left
                sound_volume = max(0, min(1, rel_x / slider_rect.width))
                return "SETTINGS"
            elif fullscreen_hovered:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
                update_display_metrics()
                return "SETTINGS"
            elif back_hovered:
                return "MENU"
        elif event.type == pygame.MOUSEMOTION:
            if dragging_slider:
                rel_x = mouse_game_pos[0] - slider_rect.left
                sound_volume = max(0, min(1, rel_x / slider_rect.width))
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_slider = False
    
    return "SETTINGS"


def handle_controls_events(back_hovered):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "QUIT"
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "MENU"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if back_hovered:
                return "MENU"

    return "CONTROLS"
 


DEBUG_SHOW_PLATFORM_NUMBERS = False
DEBUG_SHOW_HITBOX = False
DEBUG_SHOW_PLATFORM_COLLIDERS = False
DEBUG_HOT_RELOAD = True
DEBUG_TELEPORT_ON_CLICK = True
 
WORLD_HEIGHT = 9000
 
sprite_sheet = pygame.image.load("images/player_sprite.png").convert_alpha()
sprite_run = pygame.image.load("images/player_run_sprite.png").convert_alpha()
sprite_fly = pygame.image.load("images/player_fly_sprite.png").convert_alpha()
sprite_fall = pygame.image.load("images/player_fall_sprite.png").convert_alpha()
sprite_slide = pygame.image.load("images/player_slide_sprite.png").convert_alpha()
player_jump_charge = pygame.image.load("images/player_jump_charge.png").convert_alpha()
player_too_high = pygame.image.load("images/fast_fall.png").convert_alpha()
wall_grab_image = pygame.image.load("images/wall_grab.png").convert_alpha()

wall_grab_image = pygame.transform.scale(wall_grab_image, (55, 75))
player_jump_charge = pygame.transform.scale(player_jump_charge, (67, 78))
player_too_high = pygame.transform.scale(player_too_high, (100, 75))
 
frames = []
for i in range(4):
    frame = sprite_sheet.subsurface(
        (i * 212, 0, 212, 232)
    )
    frame = pygame.transform.scale(frame, (69, 75))
    frames.append(frame)
 
runframes = []
for i in range(4):
    frame = sprite_run.subsurface(
        (i * 208, 0, 208, 240)
    )
    frame = pygame.transform.scale(frame, (69, 75))
    runframes.append(frame)
 
flyframes = []
for i in range(4):
    frame = sprite_fly.subsurface(
        (i * 208, 0, 208, 240)
    )
    frame = pygame.transform.scale(frame, (69, 75))
    flyframes.append(frame)
 
fallframes = []
for i in range(4):
    frame = sprite_fall.subsurface(
        (i * 248, 0, 248, 240)
    )
    frame = pygame.transform.scale(frame, (83, 75))
    fallframes.append(frame)

slideframes = []
for i in range(4):
    frame = sprite_slide.subsurface(
        (i * 280, 0, 280, 232)
    )
    frame = pygame.transform.scale(frame, (93, 75))
    slideframes.append(frame)
 
current_frame = 0
animation_speed = 0.12
animation_timer = 0
 
SPRITE_WIDTH = 68.9
 
sprite_offset_x = -10
sprite_offset_y = -5
 
player = pygame.Rect(512, WORLD_HEIGHT - 50, 35, 70)
CAMERA_FOOT_OFFSET = 70
player_color = (255, 255, 255)
player_speed = 0.6

jump_power = 0
jump_max = 15.1
side_jump = 8
jump_left = False
jump_right = False
jump_cooldown = 0
jump_available = True
jumped = False
charged = False
jump_space_released = False

sliding = False
slide_available = True
sliding_lenght = 0
sliding_cooldown = 0

wall_grab = False
wall_grab_available = True
wall_jump_cooldown = 0
touching_wall_left = False
touching_wall_right = False
skip_collision_this_frame = False

stun = False
stun_cooldown = 0

facing_right = False

grounded = True
grounded_platform = None

player_x_before = player.x

MIN_PLATFORM_HEIGHT = 80
friction = 0.3
icy = False

player_vel_x = 0
player_vel_y = 0
gravity = 0.5

player_vel_x_before = 0
   
camera_y = 0

def export_map_to_png(platforms, filename="images/level.png"):
    map_surface = pygame.Surface((WIDTH, WORLD_HEIGHT), pygame.SRCALPHA)
    map_surface.fill((0, 0, 0, 0))

    for platform in platforms:
        pygame.draw.rect(map_surface, (160, 160, 160), platform)
        pygame.draw.rect(map_surface, (100, 100, 100), platform, 2)

    pygame.image.save(map_surface, filename)
 
platforms = [
    pygame.Rect(0, WORLD_HEIGHT - 50, 1024, 50), #0
    pygame.Rect(-50, 0, 50, 9000), #1
    pygame.Rect(1024, 0, 50, 9000), #2
    pygame.Rect(0, WORLD_HEIGHT - 268, 150, 250), #3
    pygame.Rect(320, WORLD_HEIGHT - 295, 300, 50), #4
    pygame.Rect(650, WORLD_HEIGHT - 535, 100, 30), #5
    pygame.Rect(775, WORLD_HEIGHT - 300, 250, 300), #6
    pygame.Rect(250, WORLD_HEIGHT - 940, 50, 60), #7
    pygame.Rect(0, WORLD_HEIGHT - 1050, 90, 50), #8
    pygame.Rect(945, WORLD_HEIGHT - 500, 80, 200), #9
    pygame.Rect(905, WORLD_HEIGHT - 500, 40, 30), #10
    pygame.Rect(300, WORLD_HEIGHT - 550, 230, 30), #11
    pygame.Rect(300, WORLD_HEIGHT - 940, 20, 400), #12
    pygame.Rect(300, WORLD_HEIGHT - 1200, 20, 100), #13
    pygame.Rect(580, WORLD_HEIGHT - 1300, 20, 650), #14
    pygame.Rect(320, WORLD_HEIGHT - 650, 60, 100), #15
    pygame.Rect(520, WORLD_HEIGHT - 770, 60, 30), #16
    pygame.Rect(320, WORLD_HEIGHT - 890, 60, 30), #17
    pygame.Rect(540, WORLD_HEIGHT - 1010, 60, 30), #18
    pygame.Rect(250, WORLD_HEIGHT - 1200, 70, 30), #19
    pygame.Rect(510, WORLD_HEIGHT - 1280, 70, 30), #20
    pygame.Rect(580, WORLD_HEIGHT - 1300, 60, 30), #21
    pygame.Rect(630, WORLD_HEIGHT - 1340, 10, 40), #22
    pygame.Rect(190, WORLD_HEIGHT - 1500, 100, 30), #23
    pygame.Rect(390, WORLD_HEIGHT - 1500, 100, 30), #24
    pygame.Rect(385, WORLD_HEIGHT - 1790, 80, 30), #25
    pygame.Rect(280, WORLD_HEIGHT - 1650, 170, 30), #26
    pygame.Rect(450, WORLD_HEIGHT - 2408, 60, 30), #27
    pygame.Rect(400, WORLD_HEIGHT - 2050, 50, 130), #28
    pygame.Rect(207, WORLD_HEIGHT - 1970, 100, 80), #29
    pygame.Rect(300, WORLD_HEIGHT - 2128, 150, 80), #30
    pygame.Rect(430, WORLD_HEIGHT - 2408, 20, 280), #31
    pygame.Rect(320, WORLD_HEIGHT - 2355, 20, 30), #32
    pygame.Rect(220, WORLD_HEIGHT - 2630, 120, 40), #33
    pygame.Rect(500, WORLD_HEIGHT - 2720, 90, 30), #34
    pygame.Rect(360, WORLD_HEIGHT - 2900, 60, 30), #35
    pygame.Rect(600, WORLD_HEIGHT - 3000, 150, 40), #36
    pygame.Rect(210, WORLD_HEIGHT - 3050, 80, 30), #37
    pygame.Rect(360, WORLD_HEIGHT - 4000, 20, 800), #38
    pygame.Rect(150, WORLD_HEIGHT - 3300, 100, 30), #39
    pygame.Rect(130, WORLD_HEIGHT - 4000, 20, 800), #40
    pygame.Rect(150, WORLD_HEIGHT - 3450, 100, 30), #41
    pygame.Rect(215, WORLD_HEIGHT - 3680, 80, 40), #42
    pygame.Rect(330, WORLD_HEIGHT - 3760, 30, 30), #43
    pygame.Rect(130, WORLD_HEIGHT - 4000, 120, 120), #44
    pygame.Rect(0, WORLD_HEIGHT - 4120, 50, 80), #45
    pygame.Rect(130, WORLD_HEIGHT - 4400, 220, 50), #46
    pygame.Rect(250, WORLD_HEIGHT - 4600, 400, 40), #47
    pygame.Rect(420, WORLD_HEIGHT - 4780, 20, 130), #48
    pygame.Rect(0, WORLD_HEIGHT - 4880, 450, 100), #49
    pygame.Rect(500, WORLD_HEIGHT - 5080, 200, 40), #50
    pygame.Rect(100, WORLD_HEIGHT - 5180, 200, 40), #51
]

export_map_to_png(platforms)

if DEBUG_HOT_RELOAD:
    last_modified_time = os.path.getmtime(__file__)
    
    def reload_platforms():
        global platforms
        try:
            with open(__file__, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            in_platforms = False
            platforms_code = []
            indent_count = 0
            
            for line in lines:
                if 'platforms = [' in line:
                    in_platforms = True
                    platforms_code.append(line)
                    continue
                    
                if in_platforms:
                    platforms_code.append(line)
                    if line.strip() == ']':
                        break
            
            exec_globals = {'pygame': pygame, 'WORLD_HEIGHT': WORLD_HEIGHT}
            exec(''.join(platforms_code), exec_globals)
            platforms = exec_globals['platforms']
            print("Platforms reloaded!")
        except Exception as e:
            print(f"Failed to reload: {e}")
 
clock = pygame.time.Clock()
FPS = 60

running = True
while running:
    clock.tick(FPS)
    if game_state == "MENU":
        play_hovered, settings_hovered, controls_hovered, exit_hovered = draw_menu(screen, GAME_SURFACE)
        new_state = handle_menu_events(play_hovered, settings_hovered, controls_hovered, exit_hovered)
        if new_state == "QUIT":
            running = False
        else:
            game_state = new_state
        continue
    elif game_state == "SETTINGS":
        fullscreen_hovered, back_hovered = draw_settings(screen, GAME_SURFACE)
        new_state = handle_settings_events(fullscreen_hovered, back_hovered)
        if new_state == "QUIT":
            running = False
        else:
            game_state = new_state
        continue
    elif game_state == "CONTROLS":
        back_hovered = draw_controls(screen, GAME_SURFACE)
        new_state = handle_controls_events(back_hovered)
        if new_state == "QUIT":
            running = False
        else:
            game_state = new_state
        continue
    
    if DEBUG_HOT_RELOAD:
        try:
            current_time = os.path.getmtime(__file__)
            if current_time != last_modified_time:
                last_modified_time = current_time
                time.sleep(0.05)
                reload_platforms()
        except:
            pass
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            fullscreen = not fullscreen
            if fullscreen:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                screen = pygame.display.set_mode((WIDTH, HEIGHT))
            update_display_metrics()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            game_state = "MENU"
            continue
        
        if DEBUG_TELEPORT_ON_CLICK:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                game_x = (mouse_x - DISPLAY_OFFSET_X) / DISPLAY_SCALE
                game_y = (mouse_y - DISPLAY_OFFSET_Y) / DISPLAY_SCALE
                player.x = int(game_x - player.width // 2)
                player.y = int(game_y + camera_y - player.height // 2)
                player_vel_y = 0
                player_vel_x = 0
                print(f"Teleported to ({player.x}, {player.y})")

    if not jump_available and grounded:
        if jump_cooldown <= 0:
            jump_cooldown = 0
            jump_available = True
        else:
            jump_cooldown -= 1    
 
    if stun:
        if stun_cooldown < 0:
            stun_cooldown = 0
            stun = False
            sprite_offset_x = -13
        else:
            facing_right = False
            stun_cooldown -= 1

    if sliding:
        if sliding_lenght < 0 or player.x == player_x_before:
            sliding_lenght = 0
            sliding_cooldown = 60
            sliding = False
            player.y -= 40
            player.height = 70
        else:
            sliding_lenght -= 1

    if not slide_available and not sliding and sliding_cooldown > 0:
        if sliding_cooldown <= 1:
            sliding_cooldown = 0
            slide_available = True
        else:
            sliding_cooldown -= 1
            sprite_offset_y = -5

    if player.y < WORLD_HEIGHT - 4200 and player.y > WORLD_HEIGHT - 7000: 
        icy = True
    else:
        icy = False

    keys = pygame.key.get_pressed()
    print(jump_cooldown)
    if keys[pygame.K_a] and not jumped and grounded and not stun and not sliding and not charged:
        player_vel_x -= player_speed
        if player_vel_x < -4:
            player_vel_x = -4
        if keys[pygame.K_c] and slide_available:
            player.height = 30
            player.y += 40
            player_vel_x = -7
            sprite_offset_y = -45
            sliding = True
            sliding_lenght = 30
            slide_available = False
    if keys[pygame.K_d] and not jumped and grounded and not stun and not sliding and not charged:
        player_vel_x += player_speed
        if player_vel_x > 4:
            player_vel_x = 4
        if keys[pygame.K_c] and slide_available:
            player.height = 30
            player.y += 40
            player_vel_x = 7
            sprite_offset_y = -45
            sliding = True
            sliding_lenght = 30
            slide_available = False
   
    if not keys[pygame.K_a] and not keys[pygame.K_d] and grounded and not sliding or keys[pygame.K_a] and keys[pygame.K_d] and grounded and not sliding or keys[pygame.K_SPACE] and grounded and not sliding and jump_cooldown <= 0:
        if keys[pygame.K_SPACE]:
            if icy:
                friction = 0.1
            else:
                friction = 10
        else:
            if icy:
                friction = 0.05 
                player_speed = 0.1
            else:
                friction = 0.3
                player_speed = 0.6
        if player_vel_x > 0:
            player_vel_x -= friction
            if player_vel_x < 0:
                player_vel_x = 0
        elif player_vel_x < 0:
            player_vel_x += friction
            if player_vel_x > 0:
                player_vel_x = 0
        if player.x == player_x_before:
            player_vel_x = 0

    player_x_before = player.x
    player.x += player_vel_x
    print(player_vel_x)
 
    for platform in platforms:
        if player.colliderect(platform):
            if player_vel_x > 0:
                player.right = platform.left  
                if not grounded:
                    player_vel_x += (player_vel_x * -1.5)                    
                    sprite_offset_x = -10
                    facing_right = False
            elif player_vel_x < 0:
                player.left = platform.right
                if not grounded:
                    player_vel_x -= (player_vel_x * 1.5)                    
                    sprite_offset_x = -20
                    facing_right = True

    touching_wall_left = False
    touching_wall_right = False

    for platform in platforms:
        if platform.height >= MIN_PLATFORM_HEIGHT:
            if player.centery - 10 < platform.bottom and player.centery + 10 > platform.top:
                if abs(player.right - platform.left) <= 2:
                    touching_wall_right = True
                if abs(player.left - platform.right) <= 2:
                    touching_wall_left = True

    if jumped and not keys[pygame.K_SPACE]:
        jump_space_released = True

    can_wall_grab = (not jumped) or jump_space_released

    if not grounded and keys[pygame.K_SPACE] and (touching_wall_left or touching_wall_right) and player_vel_y < 0 and can_wall_grab:
        can_grab = False
        for platform in platforms:
            if platform.height >= MIN_PLATFORM_HEIGHT:
                if player.centery - 10 < platform.bottom and player.centery + 10 > platform.top:
                    if abs(player.right - platform.left) <= 2 or abs(player.left - platform.right) <= 2:
                        can_grab = True
                        break
        
        if can_grab:
            wall_grab = True
            if touching_wall_left:
                facing_right = True
            elif touching_wall_right:
                facing_right = False


    if grounded:
        wall_grab = False
        jump_space_released = False
    else:
        if charged:
            charged = False
            jump_power = 0
        sprite_offset_y = -5

    if not keys[pygame.K_SPACE] and wall_grab:
        player_vel_y = -10
        if touching_wall_left:
            player_vel_x = 5
            facing_right = True
            sprite_offset_x = -23
        elif touching_wall_right:
            player_vel_x = -5
            facing_right = False
            sprite_offset_x = -13
        wall_grab = False



    if keys[pygame.K_SPACE] and grounded and not stun and not sliding and jump_available:
        on_solid_platform = False
        for p in platforms:
            if player.bottom >= p.top and player.bottom <= p.top + 5 and player_vel_y >= 0:
                if player.left < p.right and player.right > p.left:
                    on_solid_platform = True
                    break
        
        if on_solid_platform:
            sprite_offset_y = -8     
            charged = True
            if keys[pygame.K_a]:
                jump_left = True
                facing_right = False
                sprite_offset_x = -10
            if keys[pygame.K_d]:
                jump_right = True
                facing_right = True
                sprite_offset_x = -23
            if jump_power < jump_max:
                jump_power += 0.4
            elif jump_power > jump_max:
                jump_power = jump_max
            if side_jump < 4:
                side_jump = 4
            else:
                side_jump -= 0.105

   
    if not keys[pygame.K_SPACE] and jump_power > 0 and not stun and not sliding or jump_power == jump_max :  
        sprite_offset_y = -5 
        charged = False     
        player_vel_y -= jump_power
        grounded = False
        jump_available = False
        jumped = True
        jump_space_released = False
        jump_power = 0
        if not keys[pygame.K_a]:
            jump_left = False
        if not keys[pygame.K_d]:
            jump_right = False
        if jump_left == True:
            player_vel_x = -side_jump
            jump_left = False
        elif jump_right == True:
            player_vel_x = side_jump
        else:
            player_vel_x = 0
        max_right, max_left = 10, -10
        side_jump = 8

    if wall_grab:
        player_vel_y = 1
        player_vel_x = 0
        
        has_platform_below = False
        for platform in platforms:
            if platform.height >= MIN_PLATFORM_HEIGHT:
                if player.centery - 10 < platform.bottom and player.centery + 10 > platform.top:
                    if abs(player.right - platform.left) <= 2 or abs(player.left - platform.right) <= 2:
                        has_platform_below = True
                        break
        
        if not has_platform_below:
            wall_grab = False
            grounded = False
            grounded_platform = None
            skip_collision_this_frame = True
    else:
        if player_vel_y > 0.5:
            grounded = False
            grounded_platform = None
        player_vel_y += gravity

    player.y += player_vel_y

    for platform in platforms:
        if skip_collision_this_frame:
            continue
            
        if player.colliderect(platform):
            if player_vel_y > 0:
                if player_vel_y > 20:
                    stun = True
                    stun_cooldown = 90
                player.bottom = platform.top
                player_vel_y = 0  
                grounded = True
                grounded_platform = platform
                if grounded and jumped:
                    jump_cooldown = 15
                    jump_available = False
                    jumped = False         
            elif player_vel_y < 0:
                player.top = platform.bottom
                player_vel_y = 0
    
    skip_collision_this_frame = False

    if sliding and not grounded:
        sliding = False
        sliding_lenght = 0
        sliding_cooldown = 60
        player.y -= 40
        player.height = 70
        sprite_offset_y = -5

    animation_timer += animation_speed
    if animation_timer >= 1:
        animation_timer = 0
        current_frame = (current_frame + 1) % 4
 
    if stun:
        current_image = player_too_high         
    elif wall_grab: 
        current_image = wall_grab_image
        if facing_right:
            sprite_offset_x = - 4
        else:
            sprite_offset_x = -17
    elif charged and grounded and not stun:
        current_image = player_jump_charge
        if facing_right:
            sprite_offset_x = -23
        else:
            sprite_offset_x = -10
    elif player_vel_y < 0:
        current_image = flyframes[current_frame]
        if facing_right:
            sprite_offset_x = -23
    elif player_vel_y >= 0 and not grounded:
        current_image = fallframes[current_frame]
        if facing_right:
            sprite_offset_x = -30
    elif keys[pygame.K_a] and keys[pygame.K_d] or (keys[pygame.K_a] or player_vel_x < - 0.5) or (keys[pygame.K_d] or player_vel_x > 0.5):
        if player_vel_x < 0:
            facing_right = False
            sprite_offset_x = -13
        elif player_vel_x > 0:
            facing_right = True
            sprite_offset_x = -20
        current_image = runframes[current_frame]
        if sliding:
            current_image = slideframes[current_frame]
            if facing_right:
                sprite_offset_x = -65
            else:
                sprite_offset_x = 0
    else:
        current_image = frames[current_frame]
        if facing_right:
            sprite_offset_x = -23
    
    if facing_right:
        current_image = pygame.transform.flip(current_image, True, False)
 
    camera_y = player.bottom - HEIGHT // 2 - CAMERA_FOOT_OFFSET
 
    if camera_y < 0:
        camera_y = 0
    if camera_y > WORLD_HEIGHT - HEIGHT:
        camera_y = WORLD_HEIGHT - HEIGHT

    background(GAME_SURFACE, camera_y)
    GAME_SURFACE.blit(
        current_image,
        (
            player.x + sprite_offset_x,
            (player.y + sprite_offset_y) - camera_y
        )
    )

    if DEBUG_SHOW_HITBOX:
        pygame.draw.rect(
            GAME_SURFACE, (255, 0, 0), (player.x, player.y - camera_y, player.width, player.height), 1
        )

    if DEBUG_SHOW_PLATFORM_NUMBERS:
        font = pygame.font.Font(None, 24)
    
    for i, platform in enumerate(platforms):
        if DEBUG_SHOW_PLATFORM_COLLIDERS:
            pygame.draw.rect(GAME_SURFACE, (160, 160, 160), (platform.x, platform.y - camera_y, platform.width, platform.height))
        
        if DEBUG_SHOW_PLATFORM_NUMBERS:
            text = font.render(str(i), False, (255, 255, 0))
            text_rect = text.get_rect(center=(platform.centerx, platform.centery - camera_y))
            GAME_SURFACE.blit(text, text_rect)

    draw_platforms(GAME_SURFACE, camera_y)

    scaled_surface = pygame.transform.scale(GAME_SURFACE, (SCALED_WIDTH, SCALED_HEIGHT))
    screen.fill((0, 0, 0))
    screen.blit(scaled_surface, (DISPLAY_OFFSET_X, DISPLAY_OFFSET_Y))
    pygame.display.flip()


pygame.quit()
sys.exit()