import sys
import pygame as pg
import time

from Core.ActionQueue import ActionQueue
from Environment.Grid_Map import GridMap
from Core.Thymio_Robot import RealThymio
from Simulator.Thymio_Simulated import SimThymio
import Environment.Block_Manager as BlockManager
from Environment.a_star import astar
import Environment.Utils

# Import ONLY the class, not the old function
from PathPlanner import PathPlanner


def select_robot():
    print("Select robot mode:")
    print("1. Real Thymio")
    print("2. Simulator")

    choice = input("Enter choice: ")
    return RealThymio() if choice == "1" else SimThymio()


def main():
    robot = select_robot()
    print("Starting control loop! Press Ctrl+C to stop.")

    clock = pg.time.Clock()

    # 1. Setup Grid
    grid = GridMap(width_cells=20, height_cells=15, cell_size=50)
    robot.set_grid(grid)

    # 2. Setup Blocks (Optional, for visualization/collision)
    block_manager = BlockManager.BlockManager()
    block_manager.add_block("cube1", BlockManager.Block(7, 7, 1, 1))
    robot.set_block_manager(block_manager)

    # 3. Initialize Planner
    planner = PathPlanner(grid)
    action_queue = ActionQueue()

    # 4. Define Mission
    # Ensure these match where your robot actually is!
    robot_start = (0, 0)
    robot_angle = 0  # 0=East

    block_start = (7,7)  # Where the block is now
    block_goal = (5,5)  # Where you want it to go

    # 5. Generate ALL commands
    print(f"Generating mission from {block_start} to {block_goal}...")
    mission_queue = planner.generate_mission(robot_start, robot_angle, block_start, block_goal)

    # 6. Add to ActionQueue
    for cmd in mission_queue:
        action_queue.add(cmd)

    print("Final Command Queue:")
    action_queue.print_queue()

    # --------------------- GAME LOOP ------------------------
    last_move_time = pg.time.get_ticks()
    move_delay = 500  # 0.5 seconds per move

    while True:
        # Handle Pygame Events
        dt = clock.tick(60) / 1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        # Automated Movement Logic
        current_time = pg.time.get_ticks()
        if current_time - last_move_time > move_delay:
            if action_queue.has_next():
                action = action_queue.next()
                print(f"Executing: {action}")

                if action == "F":
                    robot.move_forward()
                elif action == "B":
                    robot.move_backward()
                elif action == "TR":
                    robot.rotate_right()
                elif action == "TL":
                    robot.rotate_left()
                elif action == "PB":
                    robot.find_block()

                last_move_time = current_time

        # Update Simulator Display
        robot.update(dt)


if __name__ == "__main__":
    main()