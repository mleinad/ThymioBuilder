# real_robot.py
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
