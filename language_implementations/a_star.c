#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define GRID_SIZE 5
#define INF 100000

typedef struct Node {
    int x, y, g, h;
    struct Node* parent;
} Node;

int manhattan(int x1, int y1, int x2, int y2) {
    return abs(x1 - x2) + abs(y1 - y2);
}

int isValid(int x, int y, int grid[GRID_SIZE][GRID_SIZE]) {
    return x >= 0 && y >= 0 && x < GRID_SIZE && y < GRID_SIZE && grid[x][y] == 0;
}

void reconstructPath(Node* current) {
    if (current == NULL) return;
    reconstructPath(current->parent);
    printf("(%d, %d) ", current->x, current->y);
}

//reference: astar function from chatgpt
void aStar(int grid[GRID_SIZE][GRID_SIZE], int start[2], int goal[2]) {
    Node* openSet[GRID_SIZE * GRID_SIZE];
    int openSetSize = 0;

    Node* startNode = malloc(sizeof(Node));
    startNode->x = start[0];
    startNode->y = start[1];
    startNode->g = 0;
    startNode->h = manhattan(start[0], start[1], goal[0], goal[1]);
    startNode->parent = NULL;

    openSet[openSetSize++] = startNode;

    while (openSetSize > 0) {
        Node* current = openSet[--openSetSize];

        if (current->x == goal[0] && current->y == goal[1]) {
            reconstructPath(current);
            return;
        }

        int neighbors[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        for (int i = 0; i < 4; i++) {
            int nx = current->x + neighbors[i][0];
            int ny = current->y + neighbors[i][1];

            if (isValid(nx, ny, grid)) {
                Node* neighbor = malloc(sizeof(Node));
                neighbor->x = nx;
                neighbor->y = ny;
                neighbor->g = current->g + 1;
                neighbor->h = manhattan(nx, ny, goal[0], goal[1]);
                neighbor->parent = current;

                openSet[openSetSize++] = neighbor;
                grid[nx][ny] = 1;
            }
        }
    }

    printf("No path found!\n");
}

int main() {
    int grid[GRID_SIZE][GRID_SIZE] = {
        {0, 0, 0, 0, 0},
        {0, 1, 1, 1, 0},
        {0, 0, 0, 0, 0},
        {0, 1, 1, 1, 0},
        {0, 0, 0, 0, 0}};
    int start[2] = {0, 0}, goal[2] = {4, 4};

    aStar(grid, start, goal);

    return 0;
}
