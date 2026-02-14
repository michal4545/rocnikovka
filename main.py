import pygame
import sys
 
pygame.init()
 
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Samurai")
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)
 
clock = pygame.time.Clock()
FPS = 60
 
WORLD_HEIGHT = 3000
 
sprite_sheet = pygame.image.load("player_sprite.png").convert_alpha()
sprite_run = pygame.image.load("player_run_sprite.png").convert_alpha()
sprite_fly = pygame.image.load("player_fly_sprite.png").convert_alpha()
sprite_fall = pygame.image.load("player_fall_sprite.png").convert_alpha()
player_jump_charge = pygame.image.load("player_jump_charge.png").convert_alpha()
player_too_high = pygame.image.load("fast_fall.png").convert_alpha()
background = pygame.image.load("background.png").convert_alpha()
 
player_jump_charge = pygame.transform.scale(player_jump_charge, (68.9, 75.4))
player_too_high = pygame.transform.scale(player_too_high, (100, 75.2))
 
frames = []
for i in range(4):
    frame = sprite_sheet.subsurface(
        (i * 212, 0, 212, 232)
    )
    frame = pygame.transform.scale(frame, (68.9, 75.4))
    frames.append(frame)
 
runframes = []
for i in range(4):
    frame = sprite_run.subsurface(
        (i * 208, 0, 208, 240)
    )
    frame = pygame.transform.scale(frame, (68.9, 75.4))
    runframes.append(frame)
 
flyframes = []
for i in range(4):
    frame = sprite_fly.subsurface(
        (i * 208, 0, 208, 240)
    )
    frame = pygame.transform.scale(frame, (68.9, 75.4))
    flyframes.append(frame)
 
fallframes = []
for i in range(4):
    frame = sprite_fall.subsurface(
        (i * 248, 0, 248, 240)
    )
    frame = pygame.transform.scale(frame, (82.9, 75.4))
    fallframes.append(frame)
 
current_frame = 0
animation_speed = 0.12
animation_timer = 0
 
SPRITE_WIDTH = 68.9
 
sprite_offset_x = -10
sprite_offset_y = -5
 
player = pygame.Rect(400, WORLD_HEIGHT - 100, 35, 70)
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

MIN_PLATFORM_WIDTH = 80

player_vel_x = 0
player_vel_y = 0
gravity = 0.5
 
camera_y = 0
 
platforms = [
    pygame.Rect(0, WORLD_HEIGHT - 50, 800, 50),
    pygame.Rect(-52, WORLD_HEIGHT - 50, 50, -1500),
    pygame.Rect(800, WORLD_HEIGHT - 100, 50, -1500),
    pygame.Rect(0, WORLD_HEIGHT - 268, 200, 250),
    pygame.Rect(340, WORLD_HEIGHT - 295, 90, 30),
    pygame.Rect(600, WORLD_HEIGHT - 300, 200, 50),
    pygame.Rect(750, WORLD_HEIGHT - 455, 50, 155),
    pygame.Rect(730, WORLD_HEIGHT - 455, 20, 30),
    pygame.Rect(400, WORLD_HEIGHT - 500, 200, 30),
    pygame.Rect(400, WORLD_HEIGHT - 940, 20, 340),
    pygame.Rect(400, WORLD_HEIGHT - 1200, 20, 100),
    pygame.Rect(580, WORLD_HEIGHT - 1200, 20, 600),
    pygame.Rect(420, WORLD_HEIGHT - 650, 60, 30),
    pygame.Rect(520, WORLD_HEIGHT - 770, 60, 30),
    pygame.Rect(420, WORLD_HEIGHT - 890, 60, 30),
    pygame.Rect(540, WORLD_HEIGHT - 1010, 60, 30),
    pygame.Rect(360, WORLD_HEIGHT - 1200, 60, 30),
    pygame.Rect(210, WORLD_HEIGHT - 1400, 100, 30),
    pygame.Rect(410, WORLD_HEIGHT - 1450, 100, 30),
    pygame.Rect(700, WORLD_HEIGHT - 1500, 100, 30),
    pygame.Rect(410, WORLD_HEIGHT - 1650, 100, 30),
    pygame.Rect(650, WORLD_HEIGHT - 1850, 100, 30),
    pygame.Rect(400, WORLD_HEIGHT - 1970, 100, 80),
    pygame.Rect(207, WORLD_HEIGHT - 1970, 100, 80),
    pygame.Rect(300, WORLD_HEIGHT - 2128, 150, 80),
    pygame.Rect(430, WORLD_HEIGHT - 2408, 20, 280),
    pygame.Rect(320, WORLD_HEIGHT - 2355, 20, 30),
]
 
running = True
while running:
    clock.tick(FPS)
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not jump_available and grounded:
        if jump_cooldown <= 0:
            jump_cooldown = 0
            jump_available = True
        else:
            jump_cooldown -= 1    
 
    if stun_cooldown < 0:
        stun_cooldown = 0
        stun = False
    else:
        stun_cooldown -= 1
 
    if sliding:
        if sliding_lenght < 0:
            sliding_lenght = 0
            sliding_cooldown = 60
            sliding = False
            player.y -= 55.4
            player.height = 75.4
            sprite_offset_y = 0
        else:
            sliding_lenght -= 1
 
    if not slide_available and not sliding:
        if sliding_cooldown <= 0:
            sliding_cooldown = 0
            slide_available = True
        else:
            sliding_cooldown -= 1
 
    keys = pygame.key.get_pressed()
 
    if keys[pygame.K_a] and not jumped and grounded and not stun and not sliding and not charged:
        player_vel_x -= player_speed
        if player_vel_x < -4:
            player_vel_x = -4
    if keys[pygame.K_d] and not jumped and grounded and not stun and not sliding and not charged:
        player_vel_x += player_speed
        if player_vel_x > 4:
            player_vel_x = 4
   
    if not keys[pygame.K_a] and not keys[pygame.K_d] and grounded and not sliding or keys[pygame.K_a] and keys[pygame.K_d]:
        if player_vel_x > 0:
            player_vel_x -= 0.3
            if player_vel_x < 0:
                player_vel_x = 0
        elif player_vel_x < 0:
            player_vel_x += 0.3
            if player_vel_x > 0:
                player_vel_x = 0
 
    player.x += player_vel_x
 
    for platform in platforms:
        if player.colliderect(platform):
            if player_vel_x > 0:
                player.right = platform.left  
                if not grounded:
                    player_vel_x += (player_vel_x * -1.3)                    
                    sprite_offset_x = -10
                    facing_right = False
            elif player_vel_x < 0:
                player.left = platform.right
                if not grounded:
                    player_vel_x -= (player_vel_x * 1.3)                    
                    sprite_offset_x = -20
                    facing_right = True

    touching_wall_left = False
    touching_wall_right = False

    for platform in platforms:
        if platform.height >= 50:
            if player.centery - 10 < platform.bottom and player.centery + 10 > platform.top:
                if abs(player.right - platform.left) <= 2:
                    touching_wall_right = True
                if abs(player.left - platform.right) <= 2:
                    touching_wall_left = True

    if not grounded and keys[pygame.K_SPACE] and (touching_wall_left or touching_wall_right):
        can_grab = False
        for platform in platforms:
            if platform.height >= 50:
                if player.centery - 10 < platform.bottom and player.centery + 10 > platform.top:
                    if abs(player.right - platform.left) <= 2 or abs(player.left - platform.right) <= 2:
                        can_grab = True
                        break
        
        if can_grab:
            wall_grab = True
            if touching_wall_left:
                facing_right = True
                sprite_offset_x = -23
            elif touching_wall_right:
                facing_right = False
                sprite_offset_x = -13

    if grounded:
        wall_grab = False

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
        charged = True
        player_vel_x = 0
        if keys[pygame.K_a]:
            jump_left = True
            facing_right = False
            sprite_offset_x = -10
        if keys[pygame.K_d]:
            jump_right = True
            facing_right = True
            sprite_offset_x = -23
        if jump_power < jump_max:
            jump_power += 0.5
        elif jump_power > jump_max:
            jump_power = jump_max
        if side_jump < 4:
            side_jump = 4
        else:
            side_jump -= 0.1

 
   
    if not keys[pygame.K_SPACE] and jump_power > 0 and not stun and not sliding:   
        charged = False     
        player_vel_y -= jump_power
        grounded = False
        jump_available = False
        jumped = True
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
            if platform.height >= 50:
                if player.centery - 10 < platform.bottom and player.centery + 10 > platform.top:
                    if abs(player.right - platform.left) <= 2 or abs(player.left - platform.right) <= 2:
                        has_platform_below = True
                        break
        
        if not has_platform_below:
            wall_grab = False
            grounded = False
            skip_collision_this_frame = True
    else:
        if player_vel_y > 0.5:
            grounded = False
        player_vel_y += gravity

    player.y += player_vel_y

    for platform in platforms:
        if skip_collision_this_frame:
            continue
            
        if player.colliderect(platform):
            if player_vel_y > 0:
                if player_vel_y > 20:
                    stun = True
                    stun_cooldown = 180
                player.bottom = platform.top
                player_vel_y = 0  
                grounded = True
                if grounded and jumped:
                    jump_cooldown = 15
                    jump_available = False
                    jumped = False         
            elif player_vel_y < 0:
                player.top = platform.bottom
                player_vel_y = 0
    
    skip_collision_this_frame = False

    animation_timer += animation_speed
    if animation_timer >= 1:
        animation_timer = 0
        current_frame = (current_frame + 1) % 4
 
    if stun:
        current_image = player_too_high
    elif keys[pygame.K_SPACE] and grounded and not stun and jump_available:
        current_image = player_jump_charge
    elif player_vel_y < 0:
        current_image = flyframes[current_frame]
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
    else:
        current_image = frames[current_frame]
        if facing_right:
            sprite_offset_x = -23
 
    if facing_right:
        current_image = pygame.transform.flip(current_image, True, False)

 
    camera_y = player.y - HEIGHT // 2
 
    if camera_y < 0:
        camera_y = 0
    if camera_y > WORLD_HEIGHT - HEIGHT:
        camera_y = WORLD_HEIGHT - HEIGHT
 

           
    """screen.blit(background, (0,- 500 - camera_y))"""
    screen.fill((0, 0, 0))
    screen.blit(
        current_image,
        (
            player.x + sprite_offset_x,
            (player.y + sprite_offset_y) - camera_y
        )
    )
 
    pygame.draw.rect(
        screen, (255, 0, 0), (player.x, player.y - camera_y, player.width, player.height), 1
    )
 
    for platform in platforms:
        pygame.draw.rect(screen, (160, 160, 160), (platform.x, platform.y - camera_y, platform.width, platform.height))
    pygame.display.flip()
 
pygame.quit()
sys.exit()