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

WORLD_HEIGHT = 1000

sprite_sheet = pygame.image.load("player_sprite.png").convert_alpha()
sprite_run = pygame.image.load("player_run_sprite.png").convert_alpha()


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

current_frame = 0
animation_speed = 0.12
animation_timer = 0

SPRITE_WIDTH = 68.9

sprite_offset_x = -10

player = pygame.Rect(400, WORLD_HEIGHT - 100, 35, 75.4)
player_color = (255, 255, 255)
player_speed = 0.6
jump_power = 0
jump_max = 13
jump_left = False
jump_right = False
grounded = True
facing_left = False

player_vel_x = 0
player_vel_y = 0
gravity = 0.5

camera_y = 0

platforms = [
    pygame.Rect(0, WORLD_HEIGHT - 50, 800, 50),
    pygame.Rect(200, 800, 200, 300),
    pygame.Rect(600, 650, 200, 35),
    pygame.Rect(500, 750, 20, 30),

]

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a] and not keys[pygame.K_SPACE] and grounded == True:
        facing_left = False
        player_vel_x -= player_speed
        sprite_offset_x = -10
        if player_vel_x < -4:
            player_vel_x = -4
    if keys[pygame.K_d] and not keys[pygame.K_SPACE] and grounded == True:
        player_vel_x += player_speed
        facing_left = True
        sprite_offset_x = -20
        if player_vel_x > 4:
            player_vel_x = 4

    
    if not keys[pygame.K_a] and not keys[pygame.K_d] and grounded == True:
        if player_vel_x > 0:
            player_vel_x -= 0.3
            if player_vel_x < 0:
                player_vel_x = 0
        elif player_vel_x < 0:
            player_vel_x += 0.3
            if player_vel_x > 0:
                player_vel_x = 0

    player.x += player_vel_x

    if keys[pygame.K_SPACE] and grounded == True:
        player_vel_x = 0
        if keys[pygame.K_a]:
            jump_left = True
        if keys[pygame.K_d]:
            jump_right = True
        if jump_power < jump_max:
            jump_power += 0.5
        elif jump_power > jump_max:
            jump_power = jump_max

    
    if not keys[pygame.K_SPACE] and jump_power > 0:        
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


    for platform in platforms:
        if player.colliderect(platform):
            if player_vel_x > 0:
                player.right = platform.left
                if not grounded:
                    player_vel_x += (player_vel_x * -1.7)
                if not keys[pygame.K_d]:
                    facing_left = False
                    sprite_offset_x = -10
            elif player_vel_x < 0:
                player.left = platform.right
                if not grounded:
                    player_vel_x -= (player_vel_x * 1.7)
                if not keys[pygame.K_a]:
                    facing_left = True
                    sprite_offset_x = -20



    player_vel_y += gravity
    player.y += player_vel_y
    if player_vel_y > 0.5:
        grounded = False

    for platform in platforms:
        if player.colliderect(platform):
            if player_vel_y > 0: 
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
    
    if player_vel_x > 0.5 or player_vel_x < -0.5:
        current_image = runframes[current_frame]
    else:
        current_image = frames[current_frame]

    if facing_left:
        current_image = pygame.transform.flip(current_image, True, False)

    camera_y = player.y - HEIGHT // 2

    if camera_y < 0:
        camera_y = 0
    if camera_y > WORLD_HEIGHT - HEIGHT:
        camera_y = WORLD_HEIGHT - HEIGHT
           
    screen.fill((0, 0, 0))
    screen.blit(
        current_image,
        (
            player.x + sprite_offset_x,
            player.y - camera_y
        )
    )

    
    """pygame.draw.rect(
        screen,
        (255, 0, 0),
        (player.x, player.y - camera_y, player.width, player.height),
        1
    )"""

    for platform in platforms:
        pygame.draw.rect(screen, (160, 160, 160), (platform.x, platform.y - camera_y, platform.width, platform.height))
    pygame.display.flip()

pygame.quit()
sys.exit()