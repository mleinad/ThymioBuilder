FREE = 0
BLOCKED = 1
UNKNOWN = -1

class GridMap:
    """Deterministic, grid-cell based occupancy map."""

    def __init__(self, width_cells, height_cells, cell_size=1):
        """
        width_cells, height_cells : int
            Number of grid cells in X and Y.
        cell_size : float
            Optional; used for display / mapping purposes.
        """
        self.width_cells = width_cells
        self.height_cells = height_cells
        self.cell_size = cell_size  # optional for scaling / visualization

        # Initialize occupancy grid (2D list)
        self.grid = [
            [FREE for _ in range(self.height_cells)]
            for _ in range(self.width_cells)
        ]

    # ---------------- Grid access -----------------
    def is_inside(self, gx, gy):
        return 0 <= gx < self.width_cells and 0 <= gy < self.height_cells

    def set_cell(self, gx, gy, value):
        if self.is_inside(gx, gy):
            self.grid[gx][gy] = value

    def get_cell(self, gx, gy):
        if self.is_inside(gx, gy):
            return self.grid[gx][gy]
        return None

    # ---------------- Block integration -----------------
    def set_block(self, block):
        """Mark all grid cells occupied by a block as BLOCKED."""
        for gx, gy in self.get_block_cells(block):
            self.set_cell(gx, gy, BLOCKED)

    def get_block_cells(self, block):
        """Return a list of grid cells covered by a block."""
        cells = []
        bb = block.bounding_box

        # Convert bounding box corners to **grid indices**
        gx_min = int(bb["left"])
        gy_min = int(bb["top"])
        gx_max = int(bb["right"])
        gy_max = int(bb["bottom"])

        # Iterate through all grid cells in bounding box
        for gx in range(gx_min, gx_max + 1):
            for gy in range(gy_min, gy_max + 1):
                if self.is_inside(gx, gy):
                    cells.append((gx, gy))

        return cells

    # ---------------- Utility -----------------
    def clear(self):
        """Set all cells to FREE."""
        for x in range(self.width_cells):
            for y in range(self.height_cells):
                self.grid[x][y] = FREE

    def print_grid(self):
        """Debug: print a simple textual map."""
        for y in range(self.height_cells):
            row = ""
            for x in range(self.width_cells):
                row += "#" if self.grid[x][y] == BLOCKED else "."
            print(row)
