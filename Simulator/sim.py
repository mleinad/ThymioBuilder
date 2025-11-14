import pygame
import sys
import math

pygame.init()

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------
WIDTH, HEIGHT = 800, 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
# -------------------------------------------------------
THYMIO_ORIGINAL = pygame.image.load("sim_assets/thymio.png").convert_alpha()
CUBE_IMG = pygame.image.load("sim_assets/cube.png").convert_alpha()

THYMIO_ORIGINAL = pygame.transform.scale(THYMIO_ORIGINAL, (100, 100))
CUBE_IMG = pygame.transform.scale(CUBE_IMG, (80, 80))

THYMIO_IMG = THYMIO_ORIGINAL.copy()

# Initial positions
thymio_rect = THYMIO_IMG.get_rect(center=(200, 300))
cube_rect   = CUBE_IMG.get_rect(center=(500, 300))



thymio_mask = pygame.mask.from_surface(THYMIO_IMG)
cube_mask = pygame.mask.from_surface(CUBE_IMG)

offset = (cube_rect.x - thymio_rect.x, cube_rect.y - thymio_rect.y)



# Draw the Thymio hitbox
pygame.draw.rect(screen, (255, 0, 0), thymio_rect, 2)  # red outline, thickness=2

# Draw the cube hitbox
pygame.draw.rect(screen, (0, 0, 255), cube_rect, 2)    # blue outline, thickness=2



# Movement speed
speed = 4
rotation_speed = 3
angle = 0  # degrees, 0 = facing right




def move_thymio_forward(distance):
    global thymio_rect, angle

    rad = math.radians(angle)
    dx = distance * math.cos(rad)
    dy = -distance * math.sin(rad)  # pygame y-axis is inverted
    thymio_rect.x += dx
    thymio_rect.y += dy

    if thymio_rect.colliderect(cube_rect):
        # Push the cube in the same direction
        cube_rect.x += dx
        cube_rect.y += dy

        cube_rect.x = max(0, min(cube_rect.x, WIDTH - cube_rect.width))
        cube_rect.y = max(0, min(cube_rect.y, HEIGHT - cube_rect.height))


def rotate_thymio(delta_deg):
    global THYMIO_IMG, thymio_rect, angle

    angle += delta_deg
    angle %= 360  # keep angle in [0, 360)

    center = thymio_rect.center
    THYMIO_IMG = pygame.transform.rotate(THYMIO_ORIGINAL, angle)
    thymio_rect = THYMIO_IMG.get_rect(center=center)





# -------------------------------------------------------# MAIN LOOP
while True:
    dt = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()




    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        move_thymio_forward(speed)
    if keys[pygame.K_DOWN]:
        move_thymio_forward(-speed)
    if keys[pygame.K_q]:
        rotate_thymio(rotation_speed)
    if keys[pygame.K_e]:
        rotate_thymio(-rotation_speed)


    collision = thymio_rect.colliderect(cube_rect)

    screen.fill((187, 218, 227))  # background color

    screen.blit(CUBE_IMG, cube_rect)
    screen.blit(THYMIO_IMG, thymio_rect)

    pygame.draw.rect(screen, (255, 0, 0), thymio_rect, 2)
    pygame.draw.rect(screen, (0, 0, 255), cube_rect, 2)

    if collision:
        pygame.draw.rect(screen, (255, 0, 0), thymio_rect, 3)
        

    pygame.display.flip()
