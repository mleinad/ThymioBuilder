# real_robot.py
from cmath import cos, sin
import math
from Core.Thymio_Interface import RobotInterface
from thymiodirect import Connection, Thymio

class RealThymio(RobotInterface):

    def __init__(self):
        port = Connection.serial_default_port()
        self.th = Thymio(serial_port=port,
                         on_connect=lambda node_id: print(f"{node_id} is connected"))
        self.th.connect()
        self.node_id = self.th.first_node()

        self._move_forward = 0
        self.th.set_variable_observer(self.node_id, self._update_thread)

    def _update_thread(self, node_id):
        if self._move_forward == 1:
            self.th[node_id]["motor.left.target"] = 10
            self.th[node_id]["motor.right.target"] = 10
        else:
            self.th[node_id]["motor.left.target"] = 0
            self.th[node_id]["motor.right.target"] = 0

  
  
  
    def move_forward(self):
        self._move_forward = 1

    def stop(self):
        self._move_forward = 0

    def get_position(self):

        return None

    def update(self, dt):
        pass  # nothing needed
    
    
    kd = 0.0000294715747
    deltaTime = 0.010  # should be update frequency 10htz (i think)
  
  
  
    # ---------------- Odometry ----------------
    def get_odometry(self):
        """Return incremental odometry (dx, dy, dtheta) since last update."""
        dleft  = self.th[self.node_id]["motor.left.speed"]  * self.kd * self.deltaTime
        dright = self.th[self.node_id]["motor.right.speed"] * self.kd * self.deltaTime

        dcenter = (dleft + dright) / 2.0
        dtheta  = (dright - dleft) / self.wheel_base

        dx = dcenter * math.cos(self.theta + dtheta/2.0)
        dy = dcenter * math.sin(self.theta + dtheta/2.0)

        return dx, dy, dtheta

    def update(self, dt):
        """Integrate odometry into global pose."""
        dx, dy, dtheta = self.get_odometry()
        self.x += dx
        self.y += dy
        self.theta += dtheta


    def get_position(self):
        """Return global pose (x, y, theta)."""
        return self.x, self.y, self.theta   
    

    def set_grid(self, grid):
        print("Grid set in RealThymio.")


    def set_path(self, path):
        print("Path set in RealThymio.")