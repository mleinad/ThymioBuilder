import time
from typing import List
from thymiodirect import Connection, Thymio

# --- CONFIGURATION CONSTANTS ---

# Motor Speed
BASE_SPEED = 200

# TIME REQUIRED TO MOVE ONE CELL (12cm) at BASE_SPEED.
CELL_MOVE_DURATION = 1.95  # seconds

# TIME REQUIRED TO PIVOT 90 DEGREES at BASE_SPEED.
TURN_90_DURATION = 1.3  # seconds

# 2. PATH PLANNING (Instruction Array)
# Define the sequence of moves the robot should perform.
TARGET_PATH: List[str] = ['F', 'TR', 'F', 'TL', 'F']


class ThymioController:
    """Manages connection, movement functions, and path execution for the Thymio robot."""

    def __init__(self):
        self.th = None
        self.node_id = None
        self.is_connected = False

    def connect(self):
        """Establishes connection to the Thymio robot."""
        try:
            port = Connection.serial_default_port()
            print(f"[INFO] Attempting connection on port: {port}")

            self.th = Thymio(serial_port=port,
                             on_connect=lambda id: print(f"\n[INFO] Thymio '{id}' connected successfully."))
            self.th.connect()

            self.node_id = self.th.first_node()
            if not self.node_id:
                raise ConnectionError("No Thymio robot found after connecting.")

            self.is_connected = True
            time.sleep(0.5)
            self.stop_motors()
            print("[INFO] Connection established and motors initialized.")
            return True

        except Exception as e:
            print(f"\n[CRITICAL ERROR] Connection Failed. Details: {e}")
            print("HINT: Ensure Thymio Suite is CLOSED to free up the USB/COM port.")
            return False

    def disconnect(self):
        """Safely stops motors and closes the connection."""
        if self.is_connected:
            self.stop_motors()
            self.th.disconnect()
            print("[INFO] Connection closed.")

    def stop_motors(self):
        """Sets both motor targets to zero."""
        if self.node_id:
            self.th[self.node_id]["motor.left.target"] = 0
            self.th[self.node_id]["motor.right.target"] = 0

    # ===================================
    # MOVEMENT FUNCTIONS (Cellular Odometry)
    # ===================================

    def _set_motors_for_duration(self, left_speed: int, right_speed: int, duration: float):
        """Utility to set motor speeds and wait for a specified duration (Odometry)."""
        if not self.is_connected: return

        self.th[self.node_id]["motor.left.target"] = left_speed
        self.th[self.node_id]["motor.right.target"] = right_speed
        time.sleep(duration)
        self.stop_motors()

    def move_forwards(self):
        """Moves one cell (12cm) forward based on calibrated time."""
        print(f"Executing: Move Forward 1 cell ({CELL_MOVE_DURATION}s)")
        self._set_motors_for_duration(BASE_SPEED, BASE_SPEED, CELL_MOVE_DURATION)

    def move_backwards(self):
        """Moves one cell (12cm) backward based on calibrated time."""
        print(f"Executing: Move Backward 1 cell ({CELL_MOVE_DURATION}s)")
        self._set_motors_for_duration(-BASE_SPEED, -BASE_SPEED, CELL_MOVE_DURATION)

    def turn_left(self):
        """Pivots 90 degrees left based on calibrated time."""
        print(f"Executing: Turn Left 90 degrees ({TURN_90_DURATION}s)")
        self._set_motors_for_duration(BASE_SPEED,BASE_SPEED, 0.4)
        self._set_motors_for_duration(-BASE_SPEED, BASE_SPEED, TURN_90_DURATION)
        self._set_motors_for_duration(-BASE_SPEED,-BASE_SPEED, 0.4)

    def turn_right(self):
        """Pivots 90 degrees right based on calibrated time."""
        print(f"Executing: Turn Right 90 degrees ({TURN_90_DURATION}s)")
        self._set_motors_for_duration(BASE_SPEED, BASE_SPEED, 0.4)
        self._set_motors_for_duration(BASE_SPEED, -BASE_SPEED, TURN_90_DURATION)
        self._set_motors_for_duration(-BASE_SPEED, -BASE_SPEED, 0.4)

    # ===================================
    # PATH EXECUTION (Array Trigger)
    # ===================================

    def execute_path(self, path: List[str]):
        """Iterates through the path array and executes movement commands."""
        command_map = {
            'F': self.move_forwards,
            'B': self.move_backwards,
            'TL': self.turn_left,
            'TR': self.turn_right,
        }

        print("\n--- BEGIN PATH EXECUTION ---")
        for i, instruction in enumerate(path):
            instruction = instruction.upper()
            if instruction in command_map:
                print(f"STEP {i + 1}: {instruction}")
                command_map[instruction]()
                time.sleep(1)
            else:
                print(f"STEP {i + 1}: ERROR - Unknown command '{instruction}'. Skipping.")

        print("--- END PATH EXECUTION ---")


def run_project():
    """Main function to initialize and run the robot controller."""
    controller = ThymioController()

    if controller.connect():
        try:
            controller.execute_path(TARGET_PATH)
        except Exception as e:
            print(f"[FATAL] Runtime error during path execution: {e}")
        finally:
            controller.disconnect()
    else:
        print("Could not start controller due to connection failure.")


if __name__ == "__main__":
    run_project()