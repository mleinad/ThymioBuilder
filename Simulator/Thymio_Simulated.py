# Simulator/Thymio_Simulated.py
import pygame, sys, math
from Environment.Grid_Map import GridMap
from Core.Thymio_Interface import RobotInterface

class SimThymio(RobotInterface):
   
   
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.FPS = 60
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Thymio Simulator")
        self.clock = pygame.time.Clock()

        # Load and scale images
        self.THYMIO_ORIGINAL = pygame.image.load("Simulator/sim_assets/thymio.png").convert_alpha()
        self.CUBE_IMG = pygame.image.load("Simulator/sim_assets/cube.png").convert_alpha()
        self.THYMIO_ORIGINAL = pygame.transform.scale(self.THYMIO_ORIGINAL, (100, 100))
        self.CUBE_IMG = pygame.transform.scale(self.CUBE_IMG, (80, 80))
        self.THYMIO_IMG = self.THYMIO_ORIGINAL.copy()

        # Initial positions
        self.thymio_rect = self.THYMIO_IMG.get_rect(center=(200, 300))
        self.cube_rect   = self.CUBE_IMG.get_rect(center=(500, 300))

        # Masks
        self.thymio_mask = pygame.mask.from_surface(self.THYMIO_IMG)
        self.cube_mask   = pygame.mask.from_surface(self.CUBE_IMG)

        # Movement
        self.speed = 100.0          # pixels per second
        self.rotation_speed = 90.0  # degrees per second
        self.angle = 0

        # Flags
        self._move_forward = False
        self._move_backward = False
        self._rotate_left = False
        self._rotate_right = False

        # Odometry state
        self.x, self.y, self.theta = self.thymio_rect.centerx, self.thymio_rect.centery, 0


        # Grid and path
        self.grid = None
        self.path = []

    # -------------- Debug --------------------
    def handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.move_forward()
        elif keys[pygame.K_DOWN]:
            self.move_backward()
        else:
            self._move_forward = False
            self._move_backward = False

        # Rotation
        if keys[pygame.K_q]:
            self.rotate_left()
        elif keys[pygame.K_e]:
            self.rotate_right()
        else:
            self._rotate_left = False
            self._rotate_right = False


    # ---------------- Grid ----------------
    def set_grid(self, grid):
        self.grid = grid

    def set_path(self, path):
        self.path = path

    def draw_grid(self, gridmap: GridMap):
        for gy in range(gridmap.height_cells):
            for gx in range(gridmap.width_cells):
                rect = pygame.Rect(
                    gx * gridmap.cell_size,
                    gy * gridmap.cell_size,
                    gridmap.cell_size,
                    gridmap.cell_size
                )
                # Draw the cell outline
                pygame.draw.rect(self.screen, (150, 150, 150), rect, 1)

        if self.path:
            for gx, gy in self.path:
                rect = pygame.Rect(
                    gx * gridmap.cell_size,
                    gy * gridmap.cell_size,
                    gridmap.cell_size,
                    gridmap.cell_size
                )
                pygame.draw.rect(self.screen, (0, 255, 0), rect)



    # ---------------- Movement ----------------
    def move_forward(self):
        self._move_forward = True
        self._move_backward = False

    def move_backward(self):
        self._move_backward = True
        self._move_forward = False

    def rotate_left(self):
        self._rotate_left = True
        self._rotate_right = False

    def rotate_right(self):
        self._rotate_right = True
        self._rotate_left = False

    def stop(self):
        self._move_forward = False
        self._move_backward = False
        self._rotate_left = False
        self._rotate_right = False

    # ---------------- Odometry ----------------
    def get_position(self):
        return self.x, self.y, math.radians(self.angle)

    def update(self, dt):

        self.handle_input()


        # rotation
        if self._rotate_left:
            self.angle = (self.angle + self.rotation_speed * dt) % 360
        if self._rotate_right:
            self.angle = (self.angle - self.rotation_speed * dt) % 360

        # forward/backward
        direction = 0
        if self._move_forward:
            direction = 1
        elif self._move_backward:
            direction = -1

        if direction != 0:
            rad = math.radians(self.angle)
            dx = direction * self.speed * dt * math.cos(rad)
            dy = -direction * self.speed * dt * math.sin(rad)

            new_rect = self.thymio_rect.copy()
            new_rect.x += dx
            new_rect.y += dy

            offset = (self.cube_rect.x - new_rect.x, self.cube_rect.y - new_rect.y)
            if self.thymio_mask.overlap(self.cube_mask, offset):
                # push cube
                self.cube_rect.x += dx
                self.cube_rect.y += dy
                self.cube_rect.x = max(0, min(self.cube_rect.x, self.WIDTH - self.cube_rect.width))
                self.cube_rect.y = max(0, min(self.cube_rect.y, self.HEIGHT - self.cube_rect.height))
            else:
                self.thymio_rect = new_rect
                self.x, self.y = self.thymio_rect.center

        # update rotated image
        center = self.thymio_rect.center
        self.THYMIO_IMG = pygame.transform.rotate(self.THYMIO_ORIGINAL, self.angle)
        self.thymio_rect = self.THYMIO_IMG.get_rect(center=center)
        self.thymio_mask = pygame.mask.from_surface(self.THYMIO_IMG)

        # render
        self.screen.fill((187,218,227))
        
        self.draw_grid(self.grid)

        self.screen.blit(self.CUBE_IMG, self.cube_rect)
        self.screen.blit(self.THYMIO_IMG, self.thymio_rect)
        
        self.draw_mask_outline(self.thymio_mask, self.thymio_rect.topleft, (255,0,0))
        self.draw_mask_outline(self.cube_mask, self.cube_rect.topleft, (0,0,255))
       

        blocked_cell = self.grid.world_to_grid(self.cube_rect.centerx, self.cube_rect.centery)
        self.grid.set_cell(blocked_cell[0], blocked_cell[1], 1)  # mark as blocked

        

        pygame.display.flip()






    # ---------------- Drawing ----------------
    def draw_mask_outline(self, mask, offset=(0,0), color=(0,255,0)):
        outline = mask.outline()
        if outline:
            shifted = [(x+offset[0], y+offset[1]) for (x,y) in outline]
            pygame.draw.polygon(self.screen, color, shifted, 2)
