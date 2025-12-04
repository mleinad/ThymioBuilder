from Core.ActionQueue import ActionQueue


def path_to_commands(path, start_angle=0):
    """
    Converts a path into an ActionQueue of movement commands.
    path: list of (x,y) grid coordinates
    start_angle: initial orientation of the robot (default 0 = facing right)
    Returns: ActionQueue instance
    """

    DIR_TO_ANGLE = {
        (1, 0): 0,    # right
        (-1, 0): 180, # left
        (0, -1): 90,  # up
        (0, 1): 270,  # down
    }

    def get_turn_actions(current, target):
        diff = (target - current) % 360
        if diff == 0:
            return []
        elif diff == 90:
            return ["TL"]
        elif diff == 180:
            return ["TL", "TL"]
        elif diff == 270:
            return ["TR"]
        return []

    queue = ActionQueue()
    angle = start_angle

    # Walk the path from point to point
    for i in range(1, len(path)):
        cx, cy = path[i - 1]
        nx, ny = path[i]

        dx = nx - cx
        dy = ny - cy
        move = (dx, dy)

        if move not in DIR_TO_ANGLE:
            print("Invalid movement:", move)
            continue

        target_angle = DIR_TO_ANGLE[move]

        # Add turns if needed
        queue.add_sequence(get_turn_actions(angle, target_angle))
        angle = target_angle

        # Add forward move
        queue.add("F")

    return queue
