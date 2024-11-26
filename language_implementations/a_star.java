import java.util.*;

class Node implements Comparable<Node> {
    int x, y, g, h;
    Node parent;

    public Node(int x, int y, int g, int h, Node parent) {
        this.x = x;
        this.y = y;
        this.g = g;
        this.h = h;
        this.parent = parent;
    }

    @Override
    public int compareTo(Node other) {
        return (this.g + this.h) - (other.g + other.h);
    }
}

public class AStar {

    private static int manhattan(int x1, int y1, int x2, int y2) {
        return Math.abs(x1 - x2) + Math.abs(y1 - y2);
    }

    private static boolean isValid(int x, int y, int[][] grid) {
        return x >= 0 && y >= 0 && x < grid.length && y < grid[0].length && grid[x][y] == 0;
    }

    //reference: astar function from chatgpt
    public static List<int[]> aStar(int[][] grid, int[] start, int[] goal) {
        PriorityQueue<Node> openSet = new PriorityQueue<>();
        boolean[][] visited = new boolean[grid.length][grid[0].length];

        openSet.add(new Node(start[0], start[1], 0, manhattan(start[0], start[1], goal[0], goal[1]), null));

        while (!openSet.isEmpty()) {
            Node current = openSet.poll();

            if (current.x == goal[0] && current.y == goal[1]) {
                List<int[]> path = new ArrayList<>();
                while (current != null) {
                    path.add(new int[]{current.x, current.y});
                    current = current.parent;
                }
                Collections.reverse(path);
                return path;
            }

            if (visited[current.x][current.y]) continue;
            visited[current.x][current.y] = true;

            int[][] neighbors = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
            for (int[] neighbor : neighbors) {
                int nx = current.x + neighbor[0];
                int ny = current.y + neighbor[1];

                if (isValid(nx, ny, grid)) {
                    openSet.add(new Node(nx, ny, current.g + 1, manhattan(nx, ny, goal[0], goal[1]), current));
                    grid[nx][ny] = 1; // Mark visited
                }
            }
        }
        return new ArrayList<>(); // No path found
    }

    public static void main(String[] args) {
        int[][] grid = {
            {0, 0, 0, 0, 0},
            {0, 1, 1, 1, 0},
            {0, 0, 0, 0, 0},
            {0, 1, 1, 1, 0},
            {0, 0, 0, 0, 0}};
        int[] start = {0, 0};
        int[] goal = {4, 4};

        List<int[]> path = aStar(grid, start, goal);

        for (int[] p : path) {
            System.out.println("(" + p[0] + ", " + p[1] + ")");
        }
    }
}
