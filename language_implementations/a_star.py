import heapq

def manhattan(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

def is_valid(x, y, grid):
    return 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] == 0

def a_star(grid, start, goal):
    open_set = []
    heapq.heappush(open_set, (0, start, 0, None))
    visited = set()

    while open_set:
        _, (x, y), g, parent = heapq.heappop(open_set)

        if (x, y) == goal:
            path = []
            while parent:
                path.append((x, y))
                x, y, g, parent = parent
            path.append(start)
            return path[::-1]

        if (x, y) in visited:
            continue
        visited.add((x, y))

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny, grid):
                heapq.heappush(open_set, (g + 1 + manhattan(nx, ny, goal[0], goal[1]), (nx, ny), g + 1, (x, y, g, parent)))
                grid[nx][ny] = 1

    return []

grid = [
    [0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0]
]
start = (0, 0)
goal = (4, 4)

path = a_star(grid, start, goal)
for step in path:
    print(step)
