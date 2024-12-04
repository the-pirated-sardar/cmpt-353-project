# cmpt-353-project

## Gather the Data
1. Navigate to the `data_gathering` folder.
2. Open a terminal in this folder.
3. Run the following command to gather the results:
   ```bash
   python run_tests.py maps/random-64-64-20.map scenarios/random-64-64-20-random-1.scen --output results.csv
4. The results will be saved as results.csv in the data_gathering folder. If results.csv already exists, it will be overwritten.

## Statistical Analysis
1. Ensure the results.csv file exists in the data_gathering folder.
2. To perform statistical analysis and generate plots:
   ```bash
   python stat_test_extended.py data_gathering/results.csv
3. All generated plots will be saved in the plots directory, created in the same location where the script is run.

## Generated Plots
The following plots are generated and saved in the plots directory:
1. Combined Histograms:
   - combined_histograms.png: Contains execution time histograms for all languages in a single figure.
2. Individual Histograms
   - Separate histogram files for each language:
     - histogram_C++.png
     - histogram_Java.png
     - histogram_JavaScript.png
     - histogram_Python.png
     - istogram_Rust.png
        
3. Heuristic Comparison Bar Chart:
    3.1. heuristic_comparison_bar_chart_updated.png: A bar chart comparing average execution times for each language across both heuristics. The averages are displayed above the bars for clarity.

## Notes
- The project supports multiple languages (C++, Java, JavaScript, Python, and Rust).
- Ensure the necessary compilers and runtime environments are installed:
  - g++ for C++
  - javac for Java
  - node for JavaScript
  - Python 3
  - cargo for Rust
- If any of the required compilers/runtimes are missing, those languages will be skipped during the execution.

## Debugging and Logs
- During the data-gathering phase (run_tests.py), logs will display which language implementations are successfully compiled and executed.
- Warnings will be displayed for skipped implementations or runtime errors.