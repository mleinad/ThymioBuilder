import math
import heapq
from Environment.a_star import astar  # Uses your existing A* for basic pathfinding


class PathPlanner:
    def __init__(self, grid):
        self.grid = grid

    # =========================================================================
    # CORE UTILITIES
    # =========================================================================

    def get_angle_between(self, p1, p2):
        """Returns the angle (0, 90, 180, 270) pointing from p1 to p2."""
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]

        if dx == 1:  return 0  # East
        if dx == -1: return 180  # West
        if dy == 1:  return 90  # South (assuming Y+ is down)
        if dy == -1: return 270  # North
        return 0

    def get_turns(self, current_angle, target_angle):
        """Returns a list of 'TR'/'TL' to align with target_angle."""
        diff = (target_angle - current_angle) % 360
        if diff == 0:   return []
        if diff == 90:  return ["TR"]
        if diff == 180: return ["TR", "TR"]  # Two rights for a 180
        if diff == 270: return ["TL"]  # 270 deg right is 90 deg left
        return []

    def get_maneuver_sequence(self, turn_type):
        """Returns the specific 'triangle dance' sequence."""
        if turn_type == "RIGHT_TURN":
            # Robot is pushing, Block turns RIGHT.
            # Robot must move to the LEFT side.
            # Sequence: Turn Right -> Move Out -> Turn Left -> Move Up -> Turn Left -> Face Block
            return ["TR", "F", "TL", "F", "TL"]

        elif turn_type == "LEFT_TURN":
            # Robot is pushing, Block turns LEFT.
            # Robot must move to the RIGHT side.
            # Sequence: Turn Left -> Move Out -> Turn Right -> Move Up -> Turn Right -> Face Block
            return ["TL", "F", "TR", "F", "TR"]
        return []

    # =========================================================================
    # PHASE 1: APPROACH (Robot -> Behind Block)
    # =========================================================================

    def generate_approach_phase(self, robot_pos, robot_angle, block_start, first_push_direction_node):
        commands = []

        # 1. Calculate the 'Docking Spot' (Where robot must stand to push)
        # Vector: Block -> Next Spot
        push_dx = first_push_direction_node[0] - block_start[0]
        push_dy = first_push_direction_node[1] - block_start[1]

        # Robot needs to be OPPOSITE to the push direction
        dock_x = block_start[0] - push_dx
        dock_y = block_start[1] - push_dy
        docking_spot = (dock_x, dock_y)

        # 2. Pathfind to Docking Spot
        # CRITICAL: Treat the block itself as an OBSTACLE so we don't crash into it.
        # We temporarily set the block cell to 1 (Blocked) in the grid.
        original_val = self.grid.get_cell(block_start[0], block_start[1])
        self.grid.set_cell(block_start[0], block_start[1], 1)

        # Use standard A* to find path
        path = astar(self.grid, robot_pos, docking_spot)

        # Restore the grid immediately
        self.grid.set_cell(block_start[0], block_start[1], original_val)

        if not path:
            print("Error: Cannot find path to docking spot!")
            return [], robot_angle  # Return empty commands

        # 3. Convert Path to Commands
        current_angle = robot_angle

        # Iterate from the 2nd node (1st is start)
        for i in range(1, len(path)):
            prev_node = path[i - 1]
            curr_node = path[i]

            # Determine required facing
            target_angle = self.get_angle_between(prev_node, curr_node)

            # Add Turns
            commands.extend(self.get_turns(current_angle, target_angle))
            current_angle = target_angle

            # Add Move
            commands.append("F")

        # 4. Final Alignment
        # Robot is at docking spot, but might not be facing the block.
        # It needs to face the block to be ready for Phase 2.
        final_face_angle = self.get_angle_between(docking_spot, block_start)
        commands.extend(self.get_turns(current_angle, final_face_angle))
        current_angle = final_face_angle

        return commands, current_angle

    # =========================================================================
    # PHASE 2: TRANSPORT (Push Block -> Goal)
    # =========================================================================

    def get_weighted_block_path(self, start, goal, turn_penalty=5.0):
        """Custom A* for the Block that penalizes turns."""

        def h(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, 0, start, None))  # (f, count, pos, last_dir)
        came_from = {}
        g_score = {start: 0}
        count = 0

        while open_set:
            _, _, current, last_dir = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    parent, d = came_from[current]
                    path.append(current)
                    current = parent
                path.append(start)
                path.reverse()
                return path

            cx, cy = current
            # Neighbors: East, West, South, North
            neighbors = [((cx + 1, cy), (1, 0)), ((cx - 1, cy), (-1, 0)),
                         ((cx, cy + 1), (0, 1)), ((cx, cy - 1), (0, -1))]

            for next_pos, direction in neighbors:
                nx, ny = next_pos
                if 0 <= nx < self.grid.width_cells and 0 <= ny < self.grid.height_cells:
                    if self.grid.get_cell(nx, ny) == 0:  # Free
                        cost = 1
                        if last_dir and last_dir != direction: cost += turn_penalty

                        new_g = g_score[current] + cost
                        if next_pos not in g_score or new_g < g_score[next_pos]:
                            g_score[next_pos] = new_g
                            heapq.heappush(open_set, (new_g + h(next_pos, goal), count, next_pos, direction))
                            came_from[next_pos] = (current, direction)
                            count += 1
        return []

    def generate_transport_phase(self, block_path):
        commands = []

        if len(block_path) < 2: return []

        # 1. Initial Push (Robot is already aligned from Phase 1)
        commands.append("F")

        # 2. Follow the path
        for i in range(1, len(block_path) - 1):
            prev = block_path[i - 1]
            curr = block_path[i]
            next_p = block_path[i + 1]

            # Vector In (Previous Move) vs Vector Out (Next Move)
            vec_in = (curr[0] - prev[0], curr[1] - prev[1])
            vec_out = (next_p[0] - curr[0], next_p[1] - curr[1])

            if vec_in == vec_out:
                # STRAIGHT
                commands.append("F")
            else:
                # TURN - Apply "Triangle Dance"
                # Cross product to determine Left vs Right turn
                # (dx1 * dy2) - (dy1 * dx2). Assuming Y+ is Down.
                cross = vec_in[0] * vec_out[1] - vec_in[1] * vec_out[0]

                if cross < 0:
                    # RIGHT TURN -> Maneuver Left
                    commands.extend(self.get_maneuver_sequence("RIGHT_TURN"))
                else:
                    # LEFT TURN -> Maneuver Right
                    commands.extend(self.get_maneuver_sequence("LEFT_TURN"))

                # Push after maneuver
                commands.append("F")

        return commands

    # =========================================================================
    # MASTER FUNCTION
    # =========================================================================

    def generate_mission(self, robot_pos, robot_angle, block_start, block_goal):
        """
        Returns the COMPLETE list of commands for the entire mission.
        """
        print(f"--- PLANNING MISSION ---")
        print(f"Robot: {robot_pos} facing {robot_angle}")
        print(f"Block: {block_start} -> {block_goal}")

        full_queue = []

        # 1. Plan Block Path
        block_path = self.get_weighted_block_path(block_start, block_goal)
        if len(block_path) < 2:
            print("Block already at goal or no path found.")
            return []

        print(f"Block Path: {block_path}")

        # 2. Phase 1: Approach
        approach_cmds, new_angle = self.generate_approach_phase(
            robot_pos, robot_angle, block_start, block_path[1]
        )
        if not approach_cmds and robot_pos != block_start:
            # If empty but not at start, pathing failed
            # If robot is already at docking spot, this is fine
            pass

        full_queue.extend(approach_cmds)
        print(f"Phase 1 (Approach): {len(approach_cmds)} moves")


        full_queue.extend(["AB"])  # Align Block + Approach Block

        # 3. Phase 2: Transport
        transport_cmds = self.generate_transport_phase(block_path)
        full_queue.extend(transport_cmds)
        print(f"Phase 2 (Transport): {len(transport_cmds)} moves")


        return full_queue