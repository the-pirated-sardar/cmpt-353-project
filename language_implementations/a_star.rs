use std::collections::BinaryHeap;
use std::cmp::Ordering;

#[derive(Eq, PartialEq)]
struct Node {
    x: usize,
    y: usize,
    g: usize,
    h: usize,
    parent: Option<Box<Node>>,
}

impl Ord for Node {
    fn cmp(&self, other: &Self) -> Ordering {
        (other.g + other.h).cmp(&(self.g + self.h))
    }
}

impl PartialOrd for Node {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

fn manhattan(x1: usize, y1: usize, x2: usize, y2: usize) -> usize {
    ((x1 as isize - x2 as isize).abs() + (y1 as isize - y2 as isize).abs()) as usize
}

fn is_valid(x: usize, y: usize, grid: &Vec<Vec<i32>>) -> bool {
    x < grid.len() && y < grid[0].len() && grid[x][y] == 0
}

fn reconstruct_path(mut current: &Node) -> Vec<(usize, usize)> {
    let mut path = Vec::new();
    while let Some(parent) = &current.parent {
        path.push((current.x, current.y));
        current = parent;
    }
    path.push((current.x, current.y));
    path.reverse();
    path
}

fn a_star(grid: &mut Vec<Vec<i32>>, start: (usize, usize), goal: (usize, usize)) -> Vec<(usize, usize)> {
    let mut open_set = BinaryHeap::new();
    open_set.push(Node {
        x: start.0,
        y: start.1,
        g: 0,
        h: manhattan(start.0, start.1, goal.0, goal.1),
        parent: None,
    });

    while let Some(current) = open_set.pop() {
        if (current.x, current.y) == goal {
            return reconstruct_path(&current);
        }

        let neighbors = [(1, 0), (-1, 0), (0, 1), (0, -1)];
        for (dx, dy) in neighbors {
            let nx = current.x as isize + dx;
            let ny = current.y as isize + dy;

            if nx >= 0 && ny >= 0 {
                let nx = nx as usize;
                let ny = ny as usize;

                if is_valid(nx, ny, grid) {
                    open_set.push(Node {
                        x: nx,
                        y: ny,
                        g: current.g + 1,
                        h: manhattan(nx, ny, goal.0, goal.1),
                        parent: Some(Box::new(current.clone())),
                    });
                    grid[nx][ny] = 1;
                }
            }
        }
    }
    Vec::new() // No path found
}

fn main() {
    let mut grid = vec![
        vec![0, 0, 0, 0, 0],
        vec![0, 1, 1, 1, 0],
        vec![0, 0, 0, 0, 0],
        vec![0, 1, 1, 1, 0],
        vec![0, 0, 0, 0, 0],
    ];
    let start = (0, 0);
    let goal = (4, 4);

    let path = a_star(&mut grid, start, goal);
    for (x, y) in path {
        println!("({}, {})", x, y);
    }
}
