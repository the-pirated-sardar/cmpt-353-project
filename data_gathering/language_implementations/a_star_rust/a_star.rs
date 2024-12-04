use std::collections::{BinaryHeap, HashSet};
use std::cmp::Ordering;
use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

const ROW: usize = 64;
const COL: usize = 64;

#[derive(Clone, PartialEq)]
struct Cell {
    parent_i: usize,
    parent_j: usize,
    f: f64,
    g: f64,
    h: f64,
}

impl Cell {
    fn new() -> Self {
        Cell {
            parent_i: 0,
            parent_j: 0,
            f: f64::INFINITY,
            g: f64::INFINITY,
            h: f64::INFINITY,
        }
    }
}

#[derive(PartialEq)]
struct PriorityQueueItem {
    priority: f64,
    position: (usize, usize),
}

impl Eq for PriorityQueueItem {}

impl Ord for PriorityQueueItem {
    fn cmp(&self, other: &Self) -> Ordering {
        // Flip the ordering because BinaryHeap is a max-heap
        other.priority.partial_cmp(&self.priority).unwrap()
    }
}

impl PartialOrd for PriorityQueueItem {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

fn is_valid(row: isize, col: isize) -> bool {
    row >= 0 && row < ROW as isize && col >= 0 && col < COL as isize
}

fn is_unblocked(grid: &[[usize; COL]], row: usize, col: usize) -> bool {
    grid[row][col] == 1
}

fn is_destination(row: usize, col: usize, dest: (usize, usize)) -> bool {
    row == dest.0 && col == dest.1
}

fn calculate_h_value(row: usize, col: usize, dest: (usize, usize), heuristic: usize) -> f64 {
    match heuristic {
        0 => (((row as isize - dest.0 as isize).pow(2)
            + (col as isize - dest.1 as isize).pow(2)) as f64)
            .sqrt(),
        _ => (row as isize - dest.0 as isize).abs() as f64
            + (col as isize - dest.1 as isize).abs() as f64,
    }
}

fn trace_path(cell_details: &[[Cell; COL]], dest: (usize, usize)) -> Vec<(usize, usize)> {
    let mut path = Vec::new();
    let mut row = dest.0;
    let mut col = dest.1;

    while !(cell_details[row][col].parent_i == row
        && cell_details[row][col].parent_j == col)
    {
        path.push((row, col));
        let temp_row = cell_details[row][col].parent_i;
        let temp_col = cell_details[row][col].parent_j;
        row = temp_row;
        col = temp_col;
    }

    path.push((row, col));
    path.reverse();
    path
}

fn a_star_search(
    grid: &[[usize; COL]],
    src: (usize, usize),
    dest: (usize, usize),
    heuristic: usize,
) -> Option<Vec<(usize, usize)>> {
    if !is_valid(src.0 as isize, src.1 as isize) || !is_valid(dest.0 as isize, dest.1 as isize) {
        return None;
    }

    if !is_unblocked(grid, src.0, src.1) || !is_unblocked(grid, dest.0, dest.1) {
        return None;
    }

    if is_destination(src.0, src.1, dest) {
        return Some(vec![src]);
    }

    let mut closed_list = vec![vec![false; COL]; ROW];
    let mut cell_details = vec![vec![Cell::new(); COL]; ROW];

    cell_details[src.0][src.1].f = 0.0;
    cell_details[src.0][src.1].g = 0.0;
    cell_details[src.0][src.1].h = 0.0;
    cell_details[src.0][src.1].parent_i = src.0;
    cell_details[src.0][src.1].parent_j = src.1;

    let mut open_list = BinaryHeap::new();
    open_list.push(PriorityQueueItem {
        priority: 0.0,
        position: src,
    });

    while let Some(current) = open_list.pop() {
        let (i, j) = current.position;

        if closed_list[i][j] {
            continue;
        }

        closed_list[i][j] = true;

        for (di, dj) in &[(0, 1), (0, -1), (1, 0), (-1, 0)] {
            let new_i = i as isize + di;
            let new_j = j as isize + dj;

            if is_valid(new_i, new_j) {
                let new_i = new_i as usize;
                let new_j = new_j as usize;

                if is_destination(new_i, new_j, dest) {
                    cell_details[new_i][new_j].parent_i = i;
                    cell_details[new_i][new_j].parent_j = j;
                    return Some(trace_path(&cell_details, dest));
                }

                if !closed_list[new_i][new_j] && is_unblocked(grid, new_i, new_j) {
                    let g_new = cell_details[i][j].g + 1.0;
                    let h_new = calculate_h_value(new_i, new_j, dest, heuristic);
                    let f_new = g_new + h_new;

                    if cell_details[new_i][new_j].f > f_new {
                        cell_details[new_i][new_j].f = f_new;
                        cell_details[new_i][new_j].g = g_new;
                        cell_details[new_i][new_j].h = h_new;
                        cell_details[new_i][new_j].parent_i = i;
                        cell_details[new_i][new_j].parent_j = j;
                        open_list.push(PriorityQueueItem {
                            priority: f_new,
                            position: (new_i, new_j),
                        });
                    }
                }
            }
        }
    }

    None
}

fn load_map(filename: &str) -> io::Result<[[usize; COL]; ROW]> {
    let mut grid = [[0; COL]; ROW];
    let file = File::open(filename)?;
    let lines = io::BufReader::new(file).lines();

    for (row, line) in lines.skip(4).enumerate() {
        for (col, char) in line?.chars().enumerate() {
            grid[row][col] = if char == '.' { 1 } else { 0 };
        }
    }

    Ok(grid)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 7 {
        eprintln!("Usage: <map_file> <start_x> <start_y> <goal_x> <goal_y> <heuristic>");
        return;
    }

    let map_file = &args[1];
    let start = (args[2].parse::<usize>().unwrap(), args[3].parse::<usize>().unwrap());
    let goal = (args[4].parse::<usize>().unwrap(), args[5].parse::<usize>().unwrap());
    let heuristic = args[6].parse::<usize>().unwrap();

    let grid = load_map(map_file).expect("Failed to load map file");

    match a_star_search(&grid, start, goal, heuristic) {
        Some(path) => println!("Path length: {}", path.len()),
        None => println!("No path found"),
    }
}
