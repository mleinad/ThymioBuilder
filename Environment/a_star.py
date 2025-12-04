import heapq
import math


## chat gpted, probably bad ----> use pathfinding.finder.a_star in the future?



def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def astar(gridmap, start, goal):

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
            # reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        cx, cy = current

        # 4-connected neighbors
        neighbors = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                if gridmap.grid[nx][ny] == 0:  # FREE
                    neighbors.append((nx, ny))

        for neighbor in neighbors:
            tentative_g = g_score[current] + 1  # cost = 1 per move
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                count += 1
                heapq.heappush(open_set, (f_score[neighbor], count, neighbor))

    # No path found
    return []
