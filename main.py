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

    grid = GridMap(width_cells=100, height_cells=100, cell_size=50)
    robot.set_grid(grid)

    block_manager = BlockManager.BlockManager()
    block_manager.add_block("cube1", BlockManager.Block(5, 3, 1, 1))
    block_manager.add_block("cube2", BlockManager.Block(6, 2, 1, 1))
    block_manager.add_block("cube3", BlockManager.Block(4, 4, 1, 1))

    grid.set_cell(0, 0, 0)
    grid.set_cell(5, 3, 1)
    grid.set_cell(6, 2, 0)
    grid.set_cell(4, 4, 1)

    robot.set_block_manager(block_manager)

    path = astar(gridmap=grid, start=(0,0), goal=(6,2))
    action_queue = Environment.Utils.path_to_commands(path, 0)

    action_queue.print_queue()

    # --------------------- COMMAND LOOP ------------------------
    while action_queue.has_next():
        action = action_queue.next()
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
        time.sleep(0.5)  # small pacing between commands

    # --------------------- PYGAME LOOP -------------------------
    while True:
        dt = clock.tick(60) / 1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
        robot.update(dt)

if __name__ == "__main__":
    main()
