import time
from typing import List
from thymiodirect import Connection, Thymio

# --- CONFIGURATION CONSTANTS ---

# Motor Speed
BASE_SPEED = -200

# TIME REQUIRED TO MOVE ONE CELL (12cm) at BASE_SPEED.
CELL_MOVE_DURATION = 1.95  # seconds

# TIME REQUIRED TO PIVOT 90 DEGREES at BASE_SPEED.
TURN_90_DURATION = 1.3  # seconds

# --- PID ALIGNMENT CONSTANTS ---

# Proportional gain (Kp) for alignment PID. Determines how aggressively the robot turns.
KP_ALIGNMENT = 0.03  # You might need to tune this value (e.g., 0.01 to 0.1)

# Maximum motor speed difference during PID control.
MAX_TURN_SPEED = 200

# Alignment control loop duration
PID_ALIGNMENT_DURATION = 10  # Maximum time to attempt alignment

# Threshold for considering alignment successful (difference between sensor readings)
ALIGNMENT_THRESHOLD = 30  # Lower value means stricter alignment

# 2. PATH PLANNING (Instruction Array)
# Define the sequence of moves the robot should perform.
TARGET_PATH: List[str] = ['A']


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
        self._set_motors_for_duration(-BASE_SPEED, -BASE_SPEED, 0.4)
        self._set_motors_for_duration(BASE_SPEED, -BASE_SPEED, TURN_90_DURATION)
        self._set_motors_for_duration(BASE_SPEED, BASE_SPEED, 0.4)

    def turn_right(self):
        """Pivots 90 degrees right based on calibrated time."""
        print(f"Executing: Turn Right 90 degrees ({TURN_90_DURATION}s)")
        self._set_motors_for_duration(-BASE_SPEED, -BASE_SPEED, 0.4)
        self._set_motors_for_duration(-BASE_SPEED, BASE_SPEED, TURN_90_DURATION)
        self._set_motors_for_duration(BASE_SPEED, BASE_SPEED, 0.4)

    # ===================================
    # ALIGNMENT FUNCTIONS (PID Control)
    # ===================================

    def align_with_block_pid(self):
        """
        Uses a Proportional (P) controller with rear sensors (prox.horizontal[5] and [6])
        to align the robot perpendicular to a detected block.
        """
        if not self.is_connected: return

        print("\n--- BEGIN PID ALIGNMENT ---")
        start_time = time.time()

        # We use a simple loop and small time steps for PID control
        while time.time() - start_time < PID_ALIGNMENT_DURATION:
            # 1. READ SENSORS
            # The sensors are indexed as follows:
            # prox.horizontal[5] -> Left-Rear sensor
            # prox.horizontal[6] -> Right-Rear sensor

            try:
                # Read the current sensor values
                left_sensor = self.th[self.node_id]["prox.horizontal"][5]
                right_sensor = self.th[self.node_id]["prox.horizontal"][6]
            except Exception as e:
                print(f"[ERROR] Could not read sensors for PID: {e}")
                self.stop_motors()
                return

            # Check if alignment is already sufficient
            error_magnitude = abs(left_sensor - right_sensor)
            if error_magnitude <= ALIGNMENT_THRESHOLD:
                print(f"[INFO] Aligned! Error magnitude: {error_magnitude}")
                break

            # 2. CALCULATE ERROR (Proportional Term)
            error = left_sensor - right_sensor

            # 3. CALCULATE CORRECTION (Motor Speed Difference)
            # Motor correction = Kp * Error
            correction = KP_ALIGNMENT * error

            # Clamp the correction to prevent overly fast turns
            correction = max(-MAX_TURN_SPEED, min(MAX_TURN_SPEED, correction))

            # 4. CALCULATE NEW MOTOR SPEEDS (Pivoting motion)
            # We want to pivot in place, so the motor speeds should be opposite.
            # BASE_SPEED is negative (-200) for forward motion, but for pivoting we
            # want to pivot slowly, let's use a small positive speed as the base
            # for the pivot, or simply rely on the correction term.

            # To pivot in place, the magnitude of speeds should be opposite and centered around 0.
            # Example: if correction is 50, Left=50, Right=-50 (Pivot CCW).
            # If correction is -50, Left=-50, Right=50 (Pivot CW).

            left_speed = int(correction)
            right_speed = int(-correction)

            # 5. APPLY NEW SPEEDS
            self.th[self.node_id]["motor.left.target"] = left_speed
            self.th[self.node_id]["motor.right.target"] = right_speed

            print(
                f"P-Control: L={left_sensor}, R={right_sensor} | Error={error:.2f} | Correction={correction:.2f} | Mtr_L={left_speed}, Mtr_R={right_speed}")

            # Small delay for the control loop frequency
            time.sleep(0.05)

        self.stop_motors()
        print("--- END PID ALIGNMENT ---")
        time.sleep(1)  # Pause after alignment

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
            'A': self.align_with_block_pid,  # New command for alignment
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
            # Example: Add 'A' to your path to test the alignment
            # TARGET_PATH = ['F', 'A', 'F']
            controller.execute_path(TARGET_PATH)
        except Exception as e:
            print(f"[FATAL] Runtime error during path execution: {e}")
        finally:
            controller.disconnect()
    else:
        print("Could not start controller due to connection failure.")


if __name__ == "__main__":
    run_project()