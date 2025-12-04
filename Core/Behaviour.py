import py_trees
from py_trees.common import Status
from math import radians
from Environment.a_star import astar
class FindBlock(py_trees.behaviour.Behaviour):
    def __init__(self, name, block_manager, current_block_ref):
        super().__init__(name)
        self.block_manager = block_manager
        self.current_block_ref = current_block_ref

    def update(self):
        # pick first unprocessed block
        for block_id, block in self.block_manager.blocks.items():
            self.current_block_ref["block"] = block
            return Status.SUCCESS
        return Status.FAILURE


class GoToBlock(py_trees.behaviour.Behaviour):
    def __init__(self, name, robot, grid, planner, get_block_fn):
        super().__init__(name)
        self.robot = robot
        self.grid = grid
        self.planner = planner
        self.get_block_fn = get_block_fn

    def update(self):
        block = self.get_block_fn()
        if not block:
            return Status.FAILURE

        # compute A* path
        start = (self.robot.grid_x, self.robot.grid_y)
        goal = (int(block.x), int(block.y))
        path = astar(self.grid, start, goal)
        if not path:
            return Status.FAILURE

        # convert path to commands
        cmds = []
        angle = self.robot.angle
        for i in range(1, len(path)):
            cx, cy = path[i-1]
            nx, ny = path[i]
            dx, dy = nx - cx, ny - cy

            desired_angle = None
            if dx == 1: desired_angle = 0
            elif dx == -1: desired_angle = 180
            elif dy == -1: desired_angle = 90
            elif dy == 1: desired_angle = 270

            # rotate commands
            diff = (desired_angle - angle) % 360
            if diff == 90 or diff == -270:
                cmds.append("TL")
                angle = (angle + 90) % 360
            elif diff == 270 or diff == -90:
                cmds.append("TR")
                angle = (angle - 90) % 360
            elif diff == 180:
                cmds.append("TR")
                cmds.append("TR")
                angle = (angle + 180) % 360

            # move forward
            cmds.append("F")

        # enqueue all commands
        self.planner.add_commands(cmds)
        return Status.SUCCESS


class FindTargetPosition(py_trees.behaviour.Behaviour):
    def __init__(self, name, grid, get_block_fn, target_pos_ref):
        super().__init__(name)
        self.grid = grid
        self.get_block_fn = get_block_fn
        self.target_pos_ref = target_pos_ref

    def update(self):
        block = self.get_block_fn()
        if not block:
            return Status.FAILURE

        # naive target: one cell to the right
        target = (int(block.x)+1, int(block.y))
        if self.grid.is_inside(*target) and self.grid.get_cell(*target) == 0:
            self.target_pos_ref["pos"] = target
            return Status.SUCCESS
        return Status.FAILURE


class PushBlockToTarget(py_trees.behaviour.Behaviour):
    def __init__(self, name, robot, grid, planner, get_block_fn, get_target_fn):
        super().__init__(name)
        self.robot = robot
        self.grid = grid
        self.planner = planner
        self.get_block_fn = get_block_fn
        self.get_target_fn = get_target_fn

    def update(self):
        block = self.get_block_fn()
        target = self.get_target_fn()
        if not block or not target:
            return Status.FAILURE

        # compute path from block to target
        start = (int(block.x), int(block.y))
        path = astar(self.grid, start, target)
        if not path:
            return Status.FAILURE

        # convert path to commands
        cmds = []
        angle = self.robot.angle
        for i in range(1, len(path)):
            cx, cy = path[i-1]
            nx, ny = path[i]
            dx, dy = nx-cx, ny-cy

            desired_angle = None
            if dx == 1: desired_angle = 0
            elif dx == -1: desired_angle = 180
            elif dy == -1: desired_angle = 90
            elif dy == 1: desired_angle = 270

            diff = (desired_angle - angle) % 360
            if diff == 90 or diff == -270:
                cmds.append("TL")
                angle = (angle + 90) % 360
            elif diff == 270 or diff == -90:
                cmds.append("TR")
                angle = (angle - 90) % 360
            elif diff == 180:
                cmds.append("TR")
                cmds.append("TR")
                angle = (angle + 180) % 360

            cmds.append("PB")  # push block instead of normal F

        # enqueue commands
        self.planner.add_commands(cmds)

        # update block position after push
        block.x, block.y = target
        self.grid.set_block(block)
        return Status.SUCCESS
