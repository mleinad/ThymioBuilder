import sys
from Environment.Grid_Map import GridMap
from Core.Thymio_Robot import RealThymio 
from Simulator.Thymio_Simulated import SimThymio
import pygame as pg

from a_star import astar

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
    
    clock = pg.time.Clock()  

    grid = GridMap(width=800, height=600, cell_size=125) #hardcoded to sprite size
    robot.set_grid(grid)

    target_x, target_y = 700, 500  # Example target position

    start_cell = robot.grid.world_to_grid(robot.x, robot.y)
    goal_cell = robot.grid.world_to_grid(target_x, target_y)

    #path = astar(robot.grid, start_cell, goal_cell)
    #robot.set_path(path)

    while True:
    
        dt = clock.tick(60) / 1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()


        
        #planing logic here    
      #  robot.move_forward()

        robot.update(dt)

        # Recalculate path every second -> very inefficient
        #    path = astar(robot.grid, start_cell, goal_cell)
        #    robot.set_path(path)


if __name__ == "__main__":
    main() 