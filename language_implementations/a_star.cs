//reference: entire A* alg from geeksforgeeks (https://www.geeksforgeeks.org/a-search-algorithm/)
using System;
using System.Collections.Generic;

public class AStarSearch
{
    // Creating a shortcut for KeyValuePair<int, int>
    public struct Pair
    {
        public int first, second;

        public Pair(int x, int y)
        {
            first = x;
            second = y;
        }
    }

    // A structure to hold the necessary parameters
    public struct Cell
    {
        // Row and Column index of its parent
        // Note that 0 <= i <= ROW-1 & 0 <= j <= COL-1
        public int parent_i, parent_j;
        // f = g + h
        public double f, g, h;
    }

    // A Function to find the shortest path between
    // a given source cell to a destination cell according
    // to A* Search Algorithm
    public static void AStar(int[,] grid, Pair src, Pair dest)
    {
        int ROW = grid.GetLength(0);
        int COL = grid.GetLength(1);

        // If the source or destination is out of range
        if (!IsValid(src.first, src.second, ROW, COL) || !IsValid(dest.first, dest.second, ROW, COL))
        {
            Console.WriteLine("Source or destination is invalid");
            return;
        }

        // Either the source or the destination is blocked
        if (!IsUnBlocked(grid, src.first, src.second) || !IsUnBlocked(grid, dest.first, dest.second))
        {
            Console.WriteLine("Source or the destination is blocked");
            return;
        }

        // If the destination cell is the same as the source cell
        if (src.first == dest.first && src.second == dest.second)
        {
            Console.WriteLine("We are already at the destination");
            return;
        }

        // Create a closed list and initialise it to false which
        // means that no cell has been included yet. This closed
        // list is implemented as a boolean 2D array
        bool[,] closedList = new bool[ROW, COL];

        // Declare a 2D array of structure to hold the details
        // of that cell
        Cell[,] cellDetails = new Cell[ROW, COL];

        for (int i = 0; i < ROW; i++)
        {
            for (int j = 0; j < COL; j++)
            {
                cellDetails[i, j].f = double.MaxValue;
                cellDetails[i, j].g = double.MaxValue;
                cellDetails[i, j].h = double.MaxValue;
                cellDetails[i, j].parent_i = -1;
                cellDetails[i, j].parent_j = -1;
            }
        }

        // Initialising the parameters of the starting node
        int x = src.first, y = src.second;
        cellDetails[x, y].f = 0.0;
        cellDetails[x, y].g = 0.0;
        cellDetails[x, y].h = 0.0;
        cellDetails[x, y].parent_i = x;
        cellDetails[x, y].parent_j = y;

        /*
            Create an open list having information as-
            <f, <i, j>>
            where f = g + h,
            and i, j are the row and column index of that cell
            Note that 0 <= i <= ROW-1 & 0 <= j <= COL-1
            This open list is implemented as a SortedSet of tuple (f, (i, j)).
            We use a custom comparer to compare tuples based on their f values.
        */
        SortedSet<(double, Pair)> openList = new SortedSet<(double, Pair)>(
            Comparer<(double, Pair)>.Create((a, b) => a.Item1.CompareTo(b.Item1)));

        // Put the starting cell on the open list and set its
        // 'f' as 0
        openList.Add((0.0, new Pair(x, y)));

        // We set this boolean value as false as initially
        // the destination is not reached.
        bool foundDest = false;

        while (openList.Count > 0)
        {
            (double f, Pair pair) p = openList.Min;
            openList.Remove(p);

            // Add this vertex to the closed list
            x = p.pair.first;
            y = p.pair.second;
            closedList[x, y] = true;

            // Generating all the 8 successors of this cell
            for (int i = -1; i <= 1; i++)
            {
                for (int j = -1; j <= 1; j++)
                {
                    if (i == 0 && j == 0)
                        continue;

                    int newX = x + i;
                    int newY = y + j;

                    // If this successor is a valid cell
                    if (IsValid(newX, newY, ROW, COL))
                    {
                        // If the destination cell is the same as the
                        // current successor
                        if (IsDestination(newX, newY, dest))
                        {
                            cellDetails[newX, newY].parent_i = x;
                            cellDetails[newX, newY].parent_j = y;
                            Console.WriteLine("The destination cell is found");
                            TracePath(cellDetails, dest);
                            foundDest = true;
                            return;
                        }

                        // If the successor is already on the closed
                        // list or if it is blocked, then ignore it.
                        if (!closedList[newX, newY] && IsUnBlocked(grid, newX, newY))
                        {
                            double gNew = cellDetails[x, y].g + 1.0;
                            double hNew = CalculateHValue(newX, newY, dest);
                            double fNew = gNew + hNew;

                            // If it isn’t on the open list, add it to
                            // the open list. Make the current square
                            // the parent of this square. Record the
                            // f, g, and h costs of the square cell
                            if (cellDetails[newX, newY].f == double.MaxValue || cellDetails[newX, newY].f > fNew)
                            {
                                openList.Add((fNew, new Pair(newX, newY)));

                                // Update the details of this cell
                                cellDetails[newX, newY].f = fNew;
                                cellDetails[newX, newY].g = gNew;
                                cellDetails[newX, newY].h = hNew;
                                cellDetails[newX, newY].parent_i = x;
                                cellDetails[newX, newY].parent_j = y;
                            }
                        }
                    }
                }
            }
        }

        // When the destination cell is not found and the open
        // list is empty, then we conclude that we failed to
        // reach the destination cell. This may happen when the
        // there is no way to destination cell (due to
        // blockages)
        if (!foundDest)
            Console.WriteLine("Failed to find the Destination Cell");
    }

    // A Utility Function to check whether given cell (row, col)
    // is a valid cell or not.
    public static bool IsValid(int row, int col, int ROW, int COL)
    {
        // Returns true if row number and column number
        // is in range
        return (row >= 0) && (row < ROW) && (col >= 0) && (col < COL);
    }

    // A Utility Function to check whether the given cell is
    // blocked or not
    public static bool IsUnBlocked(int[,] grid, int row, int col)
    {
        // Returns true if the cell is not blocked else false
        return grid[row, col] == 1;
    }

    // A Utility Function to check whether destination cell has
    // been reached or not
    public static bool IsDestination(int row, int col, Pair dest)
    {
        return (row == dest.first && col == dest.second);
    }

    // A Utility Function to calculate the 'h' heuristics.
    public static double CalculateHValue(int row, int col, Pair dest)
    {
        // Return using the distance formula
        return Math.Sqrt(Math.Pow(row - dest.first, 2) + Math.Pow(col - dest.second, 2));
    }

    // A Utility Function to trace the path from the source
    // to destination
    public static void TracePath(Cell[,] cellDetails, Pair dest)
    {
        Console.WriteLine("\nThe Path is ");
        int ROW = cellDetails.GetLength(0);
        int COL = cellDetails.GetLength(1);

        int row = dest.first;
        int col = dest.second;

        Stack<Pair> Path = new Stack<Pair>();

        while (!(cellDetails[row, col].parent_i == row && cellDetails[row, col].parent_j == col))
        {
            Path.Push(new Pair(row, col));
            int temp_row = cellDetails[row, col].parent_i;
            int temp_col = cellDetails[row, col].parent_j;
            row = temp_row;
            col = temp_col;
        }

        Path.Push(new Pair(row, col));
        while (Path.Count > 0)
        {
            Pair p = Path.Peek();
            Path.Pop();
            Console.Write(" -> ({0},{1}) ", p.first, p.second);
        }
    }

    public static void Main(string[] args)
    {

    }
}