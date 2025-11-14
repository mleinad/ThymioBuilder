# sim_robot.py
from Thymio_Interface import RobotInterface

class SimThymio(RobotInterface):

    def __init__(self):
        self.x = 0
        self.y = 0
        self.speed = 0.1
        self.moving = False

    def move_forward(self):
        self.moving = True

    def stop(self):
        self.moving = False

    def update(self, dt):
        if self.moving:
            self.x += self.speed * dt

    def get_position(self):
        return (self.x, self.y)
