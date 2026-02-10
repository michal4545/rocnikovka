import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jump King Clone")

clock = pygame.time.Clock()
FPS = 60

player_size = 40
player = pygame.Rect(WIDTH // 2, HEIGHT - 150, player_size, player_size)
player_color = (255, 255, 255)
player_speed = 1
jump_power = 0
jump_max = 20

player_vel_x = 0
player_vel_y = 0
gravity = 0.5

platforms = [
    pygame.Rect(100, 400, 20, 100),
    pygame.Rect(0, 500, 800, 20),
    pygame.Rect(500, 350, 200, 20),
    pygame.Rect(100, 50, 200, 20),
]

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a] and player_vel_x >= -2.0 and not keys[pygame.K_SPACE]:
        player_vel_x -= player_speed
    if keys[pygame.K_d] and player_vel_x <= 2.0 and not keys[pygame.K_SPACE]:
        player_vel_x += player_speed
    
    if not keys[pygame.K_a] and not keys[pygame.K_d]:
        if player_vel_x > 0:
            player_vel_x -= 0.1
            if player_vel_x < 0:
                player_vel_x = 0
        elif player_vel_x < 0:
            player_vel_x += 0.1
            if player_vel_x > 0:
                player_vel_x = 0

    player.x += player_vel_x

    if keys[pygame.K_SPACE]:
        player_vel_x = 0
        if jump_power < jump_max:
            jump_power += 1
        elif jump_power > jump_max:
            jump_power = jump_max
        
    if not keys[pygame.K_SPACE] and jump_power > 0:
        player_vel_y -= jump_power
        jump_power = 0

    player_vel_y += gravity
    player.y += player_vel_y

    for platform in platforms:
        if player.colliderect(platform):
            player_vel_x = 0
            player_vel_y = 0
            """if player_vel_y > 0:  # fallin
                player.bottom = platform.top
                player_vel_y = 0
            elif player_vel_y < 0:  # jumping up
                player.top = platform.bottom
                player_vel_y = 0"""

           
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, player_color, player)

    for platform in platforms:
        pygame.draw.rect(screen, (150, 150, 150), platform)

    pygame.display.flip()

pygame.quit()
sys.exit()