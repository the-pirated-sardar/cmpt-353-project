#include <iostream>
#include <vector>
#include <queue>
#include <tuple>
#include <cmath>
#include <unordered_map>

using namespace std;

struct Node {
    int x, y, g, h;
    bool operator<(const Node& other) const {
        return g + h > other.g + other.h;
    }
};

int manhattan(int x1, int y1, int x2, int y2) {
    return abs(x1 - x2) + abs(y1 - y2);
}

vector<pair<int, int>> neighbors = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

bool isValid(int x, int y, const vector<vector<int>>& grid) {
    return x >= 0 && y >= 0 && x < grid.size() && y < grid[0].size() && grid[x][y] == 0;
}

//reference: astar function from chatgpt
vector<pair<int, int>> aStar(vector<vector<int>>& grid, pair<int, int> start, pair<int, int> goal) {
    priority_queue<Node> openSet;
    unordered_map<int, int> cameFrom;
    openSet.push({start.first, start.second, 0, manhattan(start.first, start.second, goal.first, goal.second)});

    while (!openSet.empty()) {
        Node current = openSet.top();
        openSet.pop();
        if (current.x == goal.first && current.y == goal.second) {
            vector<pair<int, int>> path;
            while (current.g != 0) {
                path.push_back({current.x, current.y});
                int key = current.x * grid[0].size() + current.y;
                current.x = cameFrom[key] / grid[0].size();
                current.y = cameFrom[key] % grid[0].size();
            }
            path.push_back(start);
            reverse(path.begin(), path.end());
            return path;
        }

        for (auto [dx, dy] : neighbors) {
            int nx = current.x + dx, ny = current.y + dy;
            if (isValid(nx, ny, grid)) {
                int new_g = current.g + 1;
                int h = manhattan(nx, ny, goal.first, goal.second);
                openSet.push({nx, ny, new_g, h});
                cameFrom[nx * grid[0].size() + ny] = current.x * grid[0].size() + current.y;
                grid[nx][ny] = 1;
            }
        }
    }
    return {};
}

int main() {
    vector<vector<int>> grid = {
        {0, 0, 0, 0, 0},
        {0, 1, 1, 1, 0},
        {0, 0, 0, 0, 0},
        {0, 1, 1, 1, 0},
        {0, 0, 0, 0, 0}};
    pair<int, int> start = {0, 0}, goal = {4, 4};

    auto path = aStar(grid, start, goal);
    for (auto [x, y] : path) {
        cout << "(" << x << ", " << y << ") ";
    }
    return 0;
}
