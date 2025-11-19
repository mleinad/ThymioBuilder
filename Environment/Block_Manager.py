import math

class Block:
      
    def __init__(self, x, y, width, height, angle=0):
        self.x = x                  # center x
        self.y = y                  # center y
        self.width = width
        self.height = height
        self.angle = angle          # optional rotation (used in sim)


    @property
    def center(self):
        return (self.x, self.y)

    @property
    def size(self):
        return (self.width, self.height)

    @property
    def area(self):
        return self.width * self.height

    @property
    def bounding_box(self):
        return {
            "left":   self.x - self.width / 2,
            "right":  self.x + self.width / 2,
            "top":    self.y - self.height / 2,
            "bottom": self.y + self.height / 2,
        }
    

class BlockManager:

    def __init__(self):
        self.blocks = {}   # block_id -> Block instance