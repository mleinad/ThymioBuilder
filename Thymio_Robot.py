# real_robot.py
from cmath import cos, sin
from Thymio_Interface import RobotInterface
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

    def get_odometry(self):
        #check units of measurement
        global kd

        dleft = self.th[self.node_id]["motor.left.speed"] * kd * self.deltaTime
        dright = self.th[self.node_id]["motor.right.speed"] * kd * self.deltaTime

        dcenter = (dleft + dright) / 2.0

        dtheta = (dright - dleft) / 9.35  # 933mm is the distance between wheels

        dx  = dcenter * cos(dtheta/2)
        dy  = dcenter * sin(dtheta/2)

        return dx, dy, dtheta
    