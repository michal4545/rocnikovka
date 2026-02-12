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

WORLD_HEIGHT = 1500

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
sprite_offset_y = 0

player = pygame.Rect(400, WORLD_HEIGHT - 1200, 35, 75.4)
player_color = (255, 255, 255)
player_speed = 0.6
jump_power = 0
jump_max = 13
jump_left = False
jump_right = False
grounded = True
facing_right = False
stun = False
stun_cooldown = 0
sliding = False
slide_available = True
sliding_lenght = 0
sliding_cooldown = 0

player_vel_x = 0
player_vel_y = 0
gravity = 0.5

camera_y = 0

platforms = [
    pygame.Rect(0, WORLD_HEIGHT - 580, 800, 50),
    pygame.Rect(-52, WORLD_HEIGHT - 568, 50, -1500),
    pygame.Rect(800, WORLD_HEIGHT - 570, 50, -1500),
    pygame.Rect(- 32, WORLD_HEIGHT - 734, 400, 300),
    pygame.Rect(476, WORLD_HEIGHT - 848, 50, 50),
    pygame.Rect(- 32, WORLD_HEIGHT - 734, 400, 300),
    



    

]

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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

    if keys[pygame.K_a] and not keys[pygame.K_SPACE] and grounded and not stun and not sliding:
        facing_right = False
        player_vel_x -= player_speed
        sprite_offset_x = -10
        if player_vel_x < -4:
            player_vel_x = -4
        if keys[pygame.K_c] and slide_available:
            player.height = 20
            player.y += 55.4
            player_vel_x = -7
            sprite_offset_y = -55.4
            sliding = True
            sliding_lenght = 30
            slide_available = False
    if keys[pygame.K_d] and not keys[pygame.K_SPACE] and grounded and not stun and not sliding:
        player_vel_x += player_speed
        facing_right = True
        sprite_offset_x = -20
        if player_vel_x > 4:
            player_vel_x = 4
        if keys[pygame.K_c] and slide_available:
            player.height = 20
            player.y += 55.4
            player_vel_x = 7
            sprite_offset_y = -55.4
            sliding = True
            sliding_lenght = 30
            slide_available = False

    
    if not keys[pygame.K_a] and not keys[pygame.K_d] and grounded and not stun and not sliding:
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
                    player_vel_x += (player_vel_x * -2)                    
                    sprite_offset_x = -10
                    facing_right = False
            elif player_vel_x < 0:
                player.left = platform.right
                if not grounded:
                    player_vel_x -= (player_vel_x * 2)                    
                    sprite_offset_x = -20
                    facing_right = True


    if keys[pygame.K_SPACE] and grounded and not stun and not sliding:
        player_vel_x = 0
        if keys[pygame.K_a]:
            jump_left = True
            facing_right = False
            sprite_offset_x = -10
        if keys[pygame.K_d]:
            jump_right = True
            facing_right = True
            sprite_offset_x = -20
        if jump_power < jump_max:
            jump_power += 0.5
        elif jump_power > jump_max:
            jump_power = jump_max

    
    if not keys[pygame.K_SPACE] and jump_power > 0 and not stun and not sliding:        
        player_vel_y -= jump_power
        grounded = False
        jump_power = 0
        if not keys[pygame.K_a]:
            jump_left = False
        if not keys[pygame.K_d]:
            jump_right = False
        if jump_left == True:
            player_vel_x = -4
            jump_left = False
        elif jump_right == True:
            player_vel_x = 4
        else:
            player_vel_x = 0 

    player_vel_y += gravity
    player.y += player_vel_y
    if player_vel_y > 0.5:
        grounded = False

    for platform in platforms:
        if player.colliderect(platform):
            if player_vel_y > 0:
                if player_vel_y > 20:
                    stun = True
                    stun_cooldown = 180
                    player_vel_x = 0
                player.bottom = platform.top
                player_vel_y = 0
                grounded = True
            elif player_vel_y < 0: 
                player.top = platform.bottom
                player_vel_y = 0

    animation_timer += animation_speed
    if animation_timer >= 1:
        animation_timer = 0
        current_frame = (current_frame + 1) % 4

    if stun:
        current_image = player_too_high
    elif keys[pygame.K_SPACE] and grounded and not stun:
        current_image = player_jump_charge
    elif player_vel_y < 0:
        current_image = flyframes[current_frame]
    elif player_vel_y >= 0 and not grounded:
        current_image = fallframes[current_frame]
        if facing_right:
            sprite_offset_x = -30
    elif player_vel_x > 0.5 or player_vel_x < -0.5:
        current_image = runframes[current_frame]
    else:
        if facing_right:
            sprite_offset_x = -20
        current_image = frames[current_frame]

    if facing_right and not current_frame == player_too_high:
        current_image = pygame.transform.flip(current_image, True, False)

    camera_y = player.y - HEIGHT // 2

    if camera_y < 0:
        camera_y = 0
    if camera_y > WORLD_HEIGHT - HEIGHT:
        camera_y = WORLD_HEIGHT - HEIGHT

    platform_surface = pygame.Surface(
    (platform.width, platform.height),
    pygame.SRCALPHA
    )
    platform_surface.fill((200, 0, 0, 120))  # last number = transparency


           
    screen.blit(background, (0,- 500 - camera_y))
    screen.blit(
        current_image,
        (
            player.x + sprite_offset_x,
            (player.y + sprite_offset_y) - camera_y
        )
    )
    screen.blit(
        platform_surface,
        (platform.x, platform.y - camera_y)
    )

    """pygame.draw.rect(
        screen, (255, 0, 0), (player.x, player.y - camera_y, player.width, player.height), 1
    )"""

    for platform in platforms:
        """pygame.draw.rect(screen, (160, 160, 160), (platform.x, platform.y - camera_y, platform.width, platform.height))"""
    pygame.display.flip()

pygame.quit()
sys.exit()