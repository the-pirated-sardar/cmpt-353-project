import pandas as pd
import scipy.stats as stats
import argparse
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy.stats import levene
import os

def main(in_directory):
    # Create a directory for plots if it doesn't exist
    plots_dir = "plots"
    os.makedirs(plots_dir, exist_ok=True)
    
    df = pd.read_csv(in_directory)
    df = df[df['time'] > 0.0]
    
    # Combined histogram for all languages
    languages = df['language'].unique()
    figure, axes = plt.subplots(1, len(languages), figsize=(15, 6))
    
    for idx, language in enumerate(languages):
        axes[idx].hist(df[df['language'] == language]['time'], bins=25, edgecolor='grey', alpha=0.7)
        axes[idx].set_title(language)
        axes[idx].set_xlabel('Execution Time')
        axes[idx].set_ylabel('Frequency')
    plt.savefig(os.path.join(plots_dir, 'combined_histograms.png'))
    plt.close()

    # Individual histograms for each language
    for language in languages:
        plt.figure(figsize=(8, 6))
        plt.hist(df[df['language'] == language]['time'], bins=25, color='skyblue', edgecolor='grey', alpha=0.7)
        plt.title(f'Execution Time Histogram for {language}')
        plt.xlabel('Execution Time')
        plt.ylabel('Frequency')
        plt.savefig(os.path.join(plots_dir, f'histogram_{language}.png'))
        plt.close()

    # Bar chart comparing heuristics for each language with averages on top
    heuristic_means = df.groupby(['language', 'heuristic'])['time'].mean().unstack()

    # Plot bar chart
    ax = heuristic_means.plot(kind='bar', figsize=(10, 6), color=['#1f77b4', '#ff7f0e'], edgecolor='black')
    plt.title('Average Execution Time by Language and Heuristic')
    plt.xlabel('Language')
    plt.ylabel('Average Execution Time')
    plt.xticks(rotation=0)
    plt.legend(title='Heuristic', loc='upper right')

    # Add averages on top of the bars
    for i, language in enumerate(heuristic_means.index):
        for j, heuristic in enumerate(heuristic_means.columns):
            value = heuristic_means.loc[language, heuristic]
            ax.text(i + j * 0.2 - 0.1, value + 0.001, f'{value:.5f}', ha='center', va='bottom', fontsize=9)  # Slight offset

    # Save bar chart
    plt.savefig(os.path.join(plots_dir, 'heuristic_comparison_bar_chart.png'))
    plt.close()





    # Print summary statistics
    stats_summary = df.groupby("language").apply(
        lambda group: pd.Series({
            "mean": group["time"].mean(),
            "std": group["time"].std()
        })
    ).reset_index()
    print("Calculating the means and standard deviation of the algorithm implementation...")
    print(stats_summary)
    print("\n\n")

    # Perform Levene test to check for variance equality
    levene_stat, levene_pvalue = levene(
        *[df[df['language'] == lang]['time'] for lang in df['language'].unique()]
    )
    print(f"Levene p-value: {levene_pvalue}")

    # Perform Welch ANOVA
    anova_groups = stats.f_oneway(
        *[df[df['language'] == lang]['time'] for lang in df['language'].unique()]
    )
    print("\n\nPerforming ANOVA...")
    print(f"f-statistic: {anova_groups.statistic}")
    print(f"p-value: {anova_groups.pvalue:.10e}")

    # Post-hoc analysis using Tukey's HSD
    tukey = pairwise_tukeyhsd(endog=df["time"], groups=df["language"], alpha=0.05)
    print("\nTukey's HSD Test Results:")
    print(tukey)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_directory', type=str)
    args = parser.parse_args()
    main(args.in_directory)
