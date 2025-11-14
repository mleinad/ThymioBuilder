from Thymio_Robot import RealThymio 
from Simulator.Thymio_Simulated import SimThymio


def select_robot():
    print("Select robot mode:")
    print("1. Real Thymio")
    print("2. Simulator")

    choice = input("Enter choice: ")

    if choice == "1":
        return RealThymio()
    else:
        return SimThymio()


def main():
    robot = select_robot()

    print("Starting control loop! Press Ctrl+C to stop.")

    import time
    last = time.time()

    while True:
        now = time.time()
        dt = now - last
        last = now

        robot.update(dt)

        # Example:
        robot.move_forward()

        if isinstance(robot.get_position(), tuple):
            print(robot.get_position())

        time.sleep(0.05)

if __name__ == "__main__":
    main()