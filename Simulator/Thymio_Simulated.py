# Simulator/Thymio_Simplified.py
import math

import pygame, sys
from Environment.Grid_Map import GridMap
from Core.Thymio_Interface import RobotInterface
from Environment.Block_Manager import BlockManager
class SimThymio(RobotInterface):

    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Simple Thymio Simulator")

        # Grid setup
        self.grid: GridMap = None
        self.block_manager = None

        # Load images (scaled to 1 grid cell)
        self.THYMIO_IMG = pygame.image.load("Simulator/sim_assets/thymio.png").convert_alpha()
        self.CUBE_IMG = pygame.image.load("Simulator/sim_assets/cube.png").convert_alpha()

        # These will be scaled later when grid is known
        self.cell_size = None

        # Robot state (in grid coords)
        self.grid_x = 0
        self.grid_y = 0
        self.angle = 0      # 0=right, 90=up, 180=left, 270=down

        # Three cubes (in grid coords)
        self.cubes = [
            (5, 3),
            (6, 2),
            (4, 4)
        ]

    # -------------------- Setup ----------------------------

    def set_grid(self, grid: GridMap):
        self.grid = grid
        self.cell_size = grid.cell_size

        # Scale assets to grid cell size
        self.THYMIO_IMG = pygame.transform.scale(self.THYMIO_IMG, (self.cell_size, self.cell_size))
        self.CUBE_IMG = pygame.transform.scale(self.CUBE_IMG, (self.cell_size, self.cell_size))

    def set_path(self, path):
        self.path = path


    def set_block_manager(self, bm: BlockManager):
        self.block_manager = bm

    # -------------------- Movement -------------------------

    def _forward_vector(self):
        """Return dx, dy based on current angle."""
        if self.angle == 0: return (1, 0)
        if self.angle == 90: return (0, -1)
        if self.angle == 180: return (-1, 0)
        if self.angle == 270: return (0, 1)

    def _get_block_at(self, gx, gy):
        """Return block at given grid cell, or None."""
        if not self.block_manager:
            return None
        for block in self.block_manager.blocks.values():
            bx, by = int(block.x), int(block.y)
            if bx == gx and by == gy:
                return block
        return None

    def move_forward(self):
        dx, dy = self._forward_vector()
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        block = self._get_block_at(new_x, new_y)
        if block:
            # Try to push block further
            block_new_x = new_x + dx
            block_new_y = new_y + dy
            # Only push if target cell is empty
            if not self._get_block_at(block_new_x, block_new_y):
                block.x = block_new_x
                block.y = block_new_y
                # Move robot into block's old cell
                self.grid_x = new_x
                self.grid_y = new_y
        else:
            # No block, move freely
            self.grid_x = new_x
            self.grid_y = new_y

    def move_backward(self):
        dx, dy = self._forward_vector()
        new_x = self.grid_x - dx
        new_y = self.grid_y - dy

        block = self._get_block_at(new_x, new_y)
        if block:
            block_new_x = new_x - dx
            block_new_y = new_y - dy
            if not self._get_block_at(block_new_x, block_new_y):
                block.x = block_new_x
                block.y = block_new_y
                self.grid_x = new_x
                self.grid_y = new_y
        else:
            self.grid_x = new_x
            self.grid_y = new_y

    def rotate_left(self):
        self.angle = (self.angle + 90) % 360

    def rotate_right(self):
        self.angle = (self.angle - 90) % 360

    def find_block(self):
        """Simply turn around 180 degrees."""
        self.angle = (self.angle + 180) % 360

    # -------------------- Odometry -------------------------

    def get_position(self):
        """Return pixel center + heading in radians."""
        px = self.grid_x * self.cell_size + self.cell_size // 2
        py = self.grid_y * self.cell_size + self.cell_size // 2
        return px, py, math.radians(self.angle)

    # -------------------- Render ---------------------------

    def draw_grid(self):
        for gy in range(self.grid.height_cells):
            for gx in range(self.grid.width_cells):
                rect = pygame.Rect(
                    gx * self.cell_size,
                    gy * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                pygame.draw.rect(self.screen, (180, 180, 180), rect, 1)

    def draw_blocks(self):
        if not self.block_manager:
            return

        for block_id, block in self.block_manager.blocks.items():
            gx, gy = block.x, block.y  # grid coordinates
            px = gx * self.cell_size
            py = gy * self.cell_size

            # draw block as 1×1 cell
            self.screen.blit(self.CUBE_IMG, (px, py))



    def draw_thymio(self):
        rotated = pygame.transform.rotate(self.THYMIO_IMG, -self.angle)
        px = self.grid_x * self.cell_size
        py = self.grid_y * self.cell_size

        rect = rotated.get_rect(center=(px + self.cell_size//2,
                                        py + self.cell_size//2))
        self.screen.blit(rotated, rect.topleft)

    # -------------------- Loop Update ----------------------

    def update(self, dt):
        self.screen.fill((187, 218, 227))

        self.draw_grid()
        self.draw_blocks()
        self.draw_thymio()

        pygame.display.flip()

