import time
from thymiodirect import Connection, Thymio
from typing import Optional

# --- CONFIGURATION CONSTANTS ---
BASE_SPEED = -200  # Must match BASE_SPEED in thymio_robot_controller.py
TARGET_DISTANCE_CM = 12.0  # Your defined cell size
TARGET_ANGLE_DEG = 90.0  # Your defined turn angle

# Default test values (change these if you need longer/shorter tests)
TEST_MOVE_TIME = 1.9  # Time (seconds) the robot will move for distance testing
TEST_TURN_TIME = 1.3  # Time (seconds) the robot will turn for angle testing


class CalibrationController:
    """Handles connection and execution of calibration tests."""

    def __init__(self):
        self.th: Optional[Thymio] = None
        self.node_id: Optional[str] = None
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
            print("[INFO] Connection established and ready for calibration.")
            return True

        except Exception as e:
            print(f"\n[CRITICAL ERROR] Connection Failed. Details: {e}")
            print("HINT: Ensure Thymio Suite is CLOSED to free up the USB/COM port.")
            return False

    def disconnect(self):
        """Safely stops motors and closes the connection."""
        if self.is_connected and self.th:
            self.stop_motors()
            self.th.disconnect()
            print("[INFO] Connection closed.")

    def stop_motors(self):
        """Sets both motor targets to zero."""
        if self.node_id:
            self.th[self.node_id]["motor.left.target"] = 0
            self.th[self.node_id]["motor.right.target"] = 0

    def _set_motors_for_duration(self, left_speed: int, right_speed: int, duration: float):
        """Utility to set motor speeds for a fixed duration."""
        if not self.is_connected or not self.node_id: return

        self.th[self.node_id]["motor.left.target"] = left_speed
        self.th[self.node_id]["motor.right.target"] = right_speed
        time.sleep(duration)
        self.stop_motors()

    def calibrate_move(self):
        """Tests forward movement and calculates CELL_MOVE_DURATION."""
        print("\n=== CALIBRATION STEP 1: FORWARD MOVEMENT ===")
        print(f"Goal: Find time for {TARGET_DISTANCE_CM} cm (1 cell) at speed {BASE_SPEED}.")
        input(f"Press ENTER to move forward for {TEST_MOVE_TIME} seconds...")

        self._set_motors_for_duration(BASE_SPEED, BASE_SPEED, TEST_MOVE_TIME)

        try:
            distance_travelled = float(input("\n[MEASURE] How far did the robot travel (in cm)? "))

            if distance_travelled <= 0:
                print("Error: Distance must be positive. Please re-run.")
                return None

            # Calculate the required duration for 12cm
            new_duration = (TEST_MOVE_TIME / distance_travelled) * TARGET_DISTANCE_CM
            print(f"\n[RESULT] Measured speed: {distance_travelled / TEST_MOVE_TIME:.2f} cm/s")
            print(f"[SUCCESS] Calculated CELL_MOVE_DURATION: {new_duration:.3f} seconds")
            return new_duration

        except ValueError:
            print("Invalid input. Please enter a number.")
            return None

    def calibrate_turn(self):
        """Tests turning and calculates TURN_90_DURATION."""
        print("\n=== CALIBRATION STEP 2: 90 DEGREE TURN ===")
        print(f"Goal: Find time for {TARGET_ANGLE_DEG} degrees at speed {BASE_SPEED}.")
        print("HINT: Mark the robot's starting orientation.")
        input(f"Press ENTER to pivot turn left for {TEST_TURN_TIME} seconds...")

        # Turn Left: Left wheel backward, Right wheel forward
        self._set_motors_for_duration(BASE_SPEED,BASE_SPEED,0.4)
        self._set_motors_for_duration(-BASE_SPEED, BASE_SPEED, TEST_TURN_TIME)
        self._set_motors_for_duration(-BASE_SPEED, -BASE_SPEED, 0.4)

        try:
            angle_turned = float(input("\n[MEASURE] What angle did the robot turn (in degrees)? "))

            if abs(angle_turned) < 10:
                print("Warning: Angle measured is very small. Ensure the wheels did not slip.")
                return None

            # Calculate the required duration for 90 degrees
            new_duration = (TEST_TURN_TIME / angle_turned) * TARGET_ANGLE_DEG
            print(f"\n[RESULT] Measured turn rate: {angle_turned / TEST_TURN_TIME:.2f} deg/s")
            print(f"[SUCCESS] Calculated TURN_90_DURATION: {new_duration:.3f} seconds")
            return new_duration

        except ValueError:
            print("Invalid input. Please enter a number.")
            return None


def main_calibration():
    """Main execution block for calibration."""
    controller = CalibrationController()

    if controller.connect():
        try:
            #move_time = controller.calibrate_move()
            turn_time = controller.calibrate_turn()

            print("\n=============================================")
            #if move_time:
                #print(f"FINAL CELL_MOVE_DURATION: {move_time:.3f} seconds")
            if turn_time:
                print(f"FINAL TURN_90_DURATION:   {turn_time:.3f} seconds")
            print("\nCopy these values into your 'thymio_robot_controller.py' file.")
            print("=============================================")

        except Exception as e:
            print(f"[FATAL] Runtime error during calibration: {e}")
        finally:
            controller.disconnect()
    else:
        print("Calibration utility failed to start due to connection failure.")


if __name__ == "__main__":
    main_calibration()