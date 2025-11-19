import math

FREE = 0
BLOCKED = 1
UNKNOWN = -1

class GridMap:
    
    def __init__(self, width, height, cell_size):
        

        self.cell_size = cell_size / 2  #half robot size
        self.width_cells  = int(width  / self.cell_size)
        self.height_cells = int(height / self.cell_size)

        # initialize grid
        self.grid = [
            [FREE for _ in range(self.height_cells)]
            for _ in range(self.width_cells)
        ]

    def world_to_grid(self, x, y):
        """Convert world coordinates to grid indices."""
        return int(x / self.cell_size), int(y / self.cell_size)

    def grid_to_world_center(self, gx, gy):
        """Returns world coordinates of the center of a grid cell."""
        return (gx * self.cell_size + self.cell_size // 2,
                gy * self.cell_size + self.cell_size // 2)

    def is_inside(self, gx, gy):
        return 0 <= gx < self.width_cells and 0 <= gy < self.height_cells

    def set_cell(self, gx, gy, value):
        if self.is_inside(gx, gy):
            self.grid[gy][gx] = value

    def get_cell(self, gx, gy):
        if self.is_inside(gx, gy):
            return self.grid[gy][gx]
        return None