import argparse
import os
import subprocess
import time
import psutil
import shutil
import csv
import sys

# Add the implementations folder to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "language_implementations"))

import a_star  # Assuming this is the Python implementation

def load_map(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Skip the first 4 lines and process the rest
    grid = []
    for line in lines[4:]:  # Start reading from the 5th line (index 4)
        if not line.startswith("type"):  # Skip lines that start with "type"
            # Convert good spaces ('.') to 0 and bad spaces ('T' or '@') to 1
            grid.append([1 if char == '.' else 0 for char in line.strip()])
    
    return grid




def load_scen(filename):
    scenarios = []
    with open(filename, 'r') as f:
        for line in f.readlines()[1:]:  # Skip the header
            parts = line.split()
            scenarios.append({
                'start': (int(parts[4]), int(parts[5])),
                'goal': (int(parts[6]), int(parts[7])),
            })
    return scenarios


def compile_executables():
    executables = {}
    cpp_source = os.path.join("language_implementations", "a_star.cpp")
    java_source = os.path.join("language_implementations", "a_star.java")
    js_source = os.path.join("language_implementations", "a_star.js")

    # C++
    if shutil.which("g++"):
        cpp_exec = "a_star_cpp.exe"
        subprocess.run(["g++", "-o", cpp_exec, cpp_source], check=True)
        executables["C++"] = cpp_exec
    else:
        print("Warning: g++ not found. Skipping C++.")

    # Java
    if shutil.which("javac"):
        subprocess.run(["javac", java_source], check=True)
        executables["Java"] = "a_star"
    else:
        print("Warning: javac not found. Skipping Java.")

    # Node.js
    if shutil.which("node"):
        executables["JavaScript"] = "node"
    else:
        print("Warning: Node.js not found. Skipping JavaScript.")

    return executables


def run_astar_python(grid, start, goal):
    process = psutil.Process()
    start_time = time.time()
    a_star.aStarSearch(grid, start, goal)  # Run the search
    end_time = time.time()
    cpu_usage = process.cpu_percent(interval=None)
    return {
        "time": end_time - start_time
    }


def run_astar_executable(executable, lang, map_file, start, goal):
    if lang == "Java":
        command = ["java", "-cp", "language_implementations", executable, "Java", map_file, str(start[0]), str(start[1]), str(goal[0]), str(goal[1])]
    elif lang == "C++":
        command = [executable, "C++", map_file, str(start[0]), str(start[1]), str(goal[0]), str(goal[1])]
    elif lang == "JavaScript":
        command = ["node", os.path.join("language_implementations", "a_star.js"), map_file, str(start[0]), str(start[1]), str(goal[0]), str(goal[1])]
    else:
        command = [executable, map_file, str(start[0]), str(start[1]), str(goal[0]), str(goal[1])]

    # Track execution time and CPU usage
    process = psutil.Process()
    start_time = time.time()

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        end_time = time.time()
        cpu_usage = process.cpu_percent(interval=end_time-start_time)

        output = result.stdout.strip()

        if output:
            try:
                path_length = int(output)
                #print(f"Path Length from {lang}: {path_length}")
            except ValueError:
                # Handle case where output is not a valid integer
                #print(f"Error: Unable to convert output to an integer: '{output}'")
                path_length = -1  # Indicate an error in parsing the path length
        else:
            #print(f"Error: Empty output received from {lang}.")
            path_length = 0  # Indicate no path length found

        return {
            "time": end_time - start_time
        }
    except subprocess.CalledProcessError as e:
        print(f"Error running {lang} executable: {e}")
        return None





def benchmark_languages(map_file, scen_file):
    grid = load_map(map_file)
    scenarios = load_scen(scen_file)
    results = []

    print("Compiling executables...")
    executables = compile_executables()

    # Add Python as one of the benchmarks
    executables["Python"] = None

    instance_num = 1  # Initialize instance number for scenarios

    for scenario in scenarios:
        start = scenario['start']
        goal = scenario['goal']

        for lang, executable in executables.items():
            if lang == "Python":
                result = run_astar_python(grid, start, goal)
            else:
                result = run_astar_executable(executable, lang, map_file, start, goal)

            if result is not None:
                result.update({
                    "language": lang,
                    "instance_num": instance_num  # Add the instance number
                })
                results.append(result)
            else:
                print(f"Warning: No valid result for language {lang}, skipping.")

        # Increment instance number for each scenario
        instance_num += 1

    return results

def save_to_csv(results, output_file):
    # Check if results is empty
    if not results:
        print("Warning: No results to save.")
        return

    # Get the keys from the first result dictionary
    keys = results[0].keys()

    try:
        with open(output_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"Error while saving to CSV: {e}")



def main():
    parser = argparse.ArgumentParser(description="Run A* benchmarks on different languages.")
    parser.add_argument("map_file", type=str, help="Path to the .map file.")
    parser.add_argument("scen_file", type=str, help="Path to the .scen file.")
    parser.add_argument("--output", type=str, default="results.csv", help="Output CSV file.")
    args = parser.parse_args()

    if not os.path.exists(args.map_file):
        print(f"Error: Map file '{args.map_file}' not found.")
        return
    if not os.path.exists(args.scen_file):
        print(f"Error: Scenario file '{args.scen_file}' not found.")
        return

    print("Loading map and scenarios...")
    results = benchmark_languages(args.map_file, args.scen_file)

    print(results)
    print(f"Saving results to {args.output}...")
    save_to_csv(results, args.output)
    print("Benchmarking complete!")


if __name__ == "__main__":
    main()
