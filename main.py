import pygame
import sys
import os
import time
 
pygame.init()
 
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Samurai")
icon = pygame.image.load('images/icon.png')
pygame.display.set_icon(icon)
 
clock = pygame.time.Clock()
FPS = 60

DEBUG_SHOW_PLATFORM_NUMBERS = True
DEBUG_SHOW_HITBOX = True
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
 
player = pygame.Rect(400, WORLD_HEIGHT - 50, 35, 70)
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

def export_map_to_png(platforms, filename="images/level_map.png"):
    map_surface = pygame.Surface((WIDTH, WORLD_HEIGHT), pygame.SRCALPHA)
    map_surface.fill((0, 0, 0, 0))

    for platform in platforms:
        pygame.draw.rect(map_surface, (160, 160, 160), platform)
        pygame.draw.rect(map_surface, (100, 100, 100), platform, 2)

    pygame.image.save(map_surface, filename)
 
platforms = [
    pygame.Rect(0, WORLD_HEIGHT - 50, 800, 50), #0
    pygame.Rect(-50, 0, 50, 9000), #1
    pygame.Rect(800, 0, 50, 9000), #2
    pygame.Rect(0, WORLD_HEIGHT - 268, 150, 250), #3
    pygame.Rect(320, WORLD_HEIGHT - 295, 120, 50), #4
    pygame.Rect(550, WORLD_HEIGHT - 300, 250, 300), #5
    pygame.Rect(250, WORLD_HEIGHT - 940, 50, 60), #6
    pygame.Rect(0, WORLD_HEIGHT - 1050, 90, 50), #7
    pygame.Rect(720, WORLD_HEIGHT - 500, 80, 200), #8
    pygame.Rect(680, WORLD_HEIGHT - 500, 40, 30), #9
    pygame.Rect(300, WORLD_HEIGHT - 550, 230, 30), #10
    pygame.Rect(300, WORLD_HEIGHT - 940, 20, 400), #11
    pygame.Rect(300, WORLD_HEIGHT - 1200, 20, 100), #12
    pygame.Rect(580, WORLD_HEIGHT - 1300, 20, 650), #13
    pygame.Rect(320, WORLD_HEIGHT - 650, 60, 100), #14
    pygame.Rect(520, WORLD_HEIGHT - 770, 60, 30), #15
    pygame.Rect(320, WORLD_HEIGHT - 890, 60, 30), #16
    pygame.Rect(540, WORLD_HEIGHT - 1010, 60, 30), #17
    pygame.Rect(250, WORLD_HEIGHT - 1200, 70, 30), #18
    pygame.Rect(510, WORLD_HEIGHT - 1280, 70, 30), #19
    pygame.Rect(580, WORLD_HEIGHT - 1300, 60, 30), #20
    pygame.Rect(630, WORLD_HEIGHT - 1340, 10, 40), #21
    pygame.Rect(190, WORLD_HEIGHT - 1500, 100, 30), #22
    pygame.Rect(390, WORLD_HEIGHT - 1500, 100, 30), #23
    pygame.Rect(385, WORLD_HEIGHT - 1790, 80, 30), #24
    pygame.Rect(280, WORLD_HEIGHT - 1650, 170, 30), #25
    pygame.Rect(450, WORLD_HEIGHT - 2408, 60, 30), #26
    pygame.Rect(400, WORLD_HEIGHT - 2050, 50, 130), #27
    pygame.Rect(207, WORLD_HEIGHT - 1970, 100, 80), #28
    pygame.Rect(300, WORLD_HEIGHT - 2128, 150, 80), #29
    pygame.Rect(430, WORLD_HEIGHT - 2408, 20, 280), #30
    pygame.Rect(320, WORLD_HEIGHT - 2355, 20, 30), #31
    pygame.Rect(220, WORLD_HEIGHT - 2630, 120, 40), #32
    pygame.Rect(500, WORLD_HEIGHT - 2720, 90, 30), #33
    pygame.Rect(360, WORLD_HEIGHT - 2900, 60, 30), #34
    pygame.Rect(600, WORLD_HEIGHT - 3000, 150, 40), #35
    pygame.Rect(210, WORLD_HEIGHT - 3050, 80, 30), #36
    pygame.Rect(360, WORLD_HEIGHT - 4000, 20, 800), #37
    pygame.Rect(150, WORLD_HEIGHT - 3300, 100, 30), #38
    pygame.Rect(130, WORLD_HEIGHT - 4000, 20, 800), #39
    pygame.Rect(150, WORLD_HEIGHT - 3450, 100, 30), #40
    pygame.Rect(215, WORLD_HEIGHT - 3680, 80, 40), #41
    pygame.Rect(330, WORLD_HEIGHT - 3760, 30, 30), #42
    pygame.Rect(130, WORLD_HEIGHT - 4000, 120, 120), #43
    pygame.Rect(0, WORLD_HEIGHT - 4120, 50, 80), #44
    pygame.Rect(130, WORLD_HEIGHT - 4400, 220, 50), #45
    pygame.Rect(250, WORLD_HEIGHT - 4600, 400, 40), #46
    pygame.Rect(420, WORLD_HEIGHT - 4780, 20, 130), #47
    pygame.Rect(0, WORLD_HEIGHT - 4880, 450, 100), #48
    pygame.Rect(500, WORLD_HEIGHT - 5080, 200, 40), #49
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
 
running = True
while running:
    clock.tick(FPS)
    
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
        
        if DEBUG_TELEPORT_ON_CLICK:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                player.x = mouse_x - player.width // 2
                player.y = mouse_y + camera_y - player.height // 2
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
    print(player_vel_x)
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
   
    if not keys[pygame.K_a] and not keys[pygame.K_d] and grounded and not sliding or keys[pygame.K_a] and keys[pygame.K_d] and grounded and not sliding or keys[pygame.K_SPACE] and grounded and not sliding:
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

    player_x_before = player.x
    player.x += player_vel_x
 
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
    elif (keys[pygame.K_a] or player_vel_x < - 0.5) or (keys[pygame.K_d] or player_vel_x > 0.5):
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

    screen.fill((98, 144, 200))
    screen.blit(
        current_image,
        (
            player.x + sprite_offset_x,
            (player.y + sprite_offset_y) - camera_y
        )
    )

    if DEBUG_SHOW_HITBOX:
        pygame.draw.rect(
            screen, (255, 0, 0), (player.x, player.y - camera_y, player.width, player.height), 1
        )

    if DEBUG_SHOW_PLATFORM_NUMBERS:
        font = pygame.font.Font(None, 24)
    
    for i, platform in enumerate(platforms):
        pygame.draw.rect(screen, (160, 160, 160), (platform.x, platform.y - camera_y, platform.width, platform.height))
        
        if DEBUG_SHOW_PLATFORM_NUMBERS:
            text = font.render(str(i), True, (255, 255, 0))
            text_rect = text.get_rect(center=(platform.centerx, platform.centery - camera_y))
            screen.blit(text, text_rect)

    pygame.display.flip()


pygame.quit()
sys.exit()