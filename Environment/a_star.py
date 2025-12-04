import heapq
import math


def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)


# Added turn_penalty parameter (default 0 acts like normal A*)
def astar(gridmap, start, goal, turn_penalty=2.5):
    width = gridmap.width_cells
    height = gridmap.height_cells

    # Open set: priority queue with (f_score, count, node)
    open_set = []
    heapq.heappush(open_set, (0, 0, start))

    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    count = 0  # tie-breaker for heapq

    while open_set:
        current = heapq.heappop(open_set)[2]

        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        cx, cy = current

        # Calculate previous direction if we aren't at the start
        prev_dx, prev_dy = None, None
        if current in came_from:
            px, py = came_from[current]
            prev_dx = cx - px
            prev_dy = cy - py

        # 4-connected neighbors
        neighbors = []
        # Store direction (dx, dy) alongside the neighbor coordinates
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                if gridmap.grid[nx][ny] == 0:  # FREE
                    neighbors.append(((nx, ny), dx, dy))

        for (neighbor, dx, dy) in neighbors:

            # Base cost is 1 for the move itself
            move_cost = 1

            # Apply Turn Penalty
            # If we have a previous move, and the new move (dx, dy)
            # is different from the old one (prev_dx, prev_dy), add penalty.
            if prev_dx is not None and (prev_dx, prev_dy) != (dx, dy):
                move_cost += turn_penalty

            tentative_g = g_score[current] + move_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                count += 1
                heapq.heappush(open_set, (f_score[neighbor], count, neighbor))

    return []