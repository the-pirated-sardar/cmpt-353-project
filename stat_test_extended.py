import pandas as pd
import numpy as np
import scipy.stats as stats
import argparse
import matplotlib.pyplot as plt
import seaborn
from sklearn.neighbors import LocalOutlierFactor
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy.stats import levene
from pingouin import welch_anova, pairwise_gameshowell
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
import os

def main(in_directory):
    # Create a directory for plots if it doesn't exist
    plots_dir = "plots"
    os.makedirs(plots_dir, exist_ok=True)
    
    df = pd.read_csv(in_directory)
  
    # Data cleaning
    df = df[df['time'] > 0.0]
    # Heuristic == 0
    df_heuristic_0 = df[df['heuristic'] == 0]
    df_heuristic_0_pivot = df_heuristic_0.pivot(index='instance_num', columns='language', values='time')
    df_heuristic_0_pivot = df_heuristic_0_pivot.dropna()
    model_0 = LocalOutlierFactor(n_neighbors=20)
    y_heuristic_0 = model_0.fit_predict(df_heuristic_0_pivot.values)
    df_heuristic_0_pivot['lof_outlier'] = y_heuristic_0
    df_heuristic_0_pivot['is_anomaly'] = df_heuristic_0_pivot['lof_outlier'] == -1

    # Heuristic == 1
    df_heuristic_1 = df[df['heuristic'] == 1]
    df_heuristic_1_pivot = df_heuristic_1.pivot(index='instance_num', columns='language', values='time')
    df_heuristic_1_pivot = df_heuristic_1_pivot.dropna()
    model_1 = LocalOutlierFactor(n_neighbors=20)
    y_heuristic_1 = model_1.fit_predict(df_heuristic_1_pivot.values)
    df_heuristic_1_pivot['lof_outlier'] = y_heuristic_1
    df_heuristic_1_pivot['is_anomaly'] = df_heuristic_1_pivot['lof_outlier'] == -1

    # Combine the results
    df_cleaned = pd.concat([df_heuristic_0_pivot, df_heuristic_1_pivot])
    df_cleaned = df_cleaned.reset_index()
    
    # Melt data for visualization
    df_cleaned_melted = df_cleaned.melt(
        id_vars=['instance_num', 'is_anomaly'], 
        value_vars=[col for col in df_cleaned.columns if col not in ['lof_outlier', 'is_anomaly', 'instance_num']],
        var_name='language', 
        value_name='time'
    )
    df = df_cleaned_melted.merge(
        df[['instance_num', 'heuristic']].drop_duplicates(), 
        on='instance_num', 
        how='left'
    )

    # Plot all points, highlighting anomalies
    seaborn.set()
    plt.figure(figsize=(12, 8))

    # Scatterplot for inliers and outliers
    seaborn.scatterplot(
        data=df, 
        x='instance_num', 
        y='time', 
        hue='language', 
        style='is_anomaly', 
        markers={False: 'o', True: 'X'}, 
        palette='tab10',
        s=60,  # Marker size
        edgecolor='k',  # Black edge for points
        linewidth=0.5
    )

    # Log scale for better visualization
    plt.yscale("log")
    plt.title("Execution Time vs. Instance Number (Log Scale)")
    plt.xlabel("Instance Number")
    plt.ylabel("Execution Time (Log Scale)")
    plt.legend(title="Language", loc='upper right', bbox_to_anchor=(1.05, 1))
    plt.grid(linestyle='--', alpha=0.7)
    
    # Save plot
    plt.savefig(os.path.join(plots_dir, 'exec_time_vs_instance_num_with_anomalies.png'), dpi=300)
    plt.close()

    #update df to remove anomalies
    df = df[df['is_anomaly'] == False]
    
    # Combined histogram for all languages
    languages = df['language'].unique()
    figure, axes = plt.subplots(1, len(languages), figsize=(25, 7))
    
    for idx, language in enumerate(languages):
        language_times = df[df['language'] == language]
        language_times = language_times[language_times['time'] < language_times['time'].quantile(0.95)]
        axes[idx].hist(language_times['time'], bins=25, edgecolor='grey', alpha=0.7)
        axes[idx].set_title(language)
        axes[idx].set_xlabel('Execution Time')
        axes[idx].set_ylabel('Frequency')
        
    plt.subplots_adjust(wspace=0.5) # prevent overlap on y axis
    plt.savefig(os.path.join(plots_dir, 'combined_histograms.png'))
    plt.close()

    # Individual histograms for each language
    for language in languages:
        language_times = df[df['language'] == language]
        language_times = language_times[language_times['time'] < language_times['time'].quantile(0.95)]
        plt.hist(language_times['time'], bins=25, color='skyblue', edgecolor='grey', alpha=0.7)
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
    plt.legend(['Euclidean', 'Manhattan'], title='Heuristic', loc='upper right')

    # Add averages on top of the bars
    for i, language in enumerate(heuristic_means.index):
        for j, heuristic in enumerate(heuristic_means.columns):
            value = heuristic_means.loc[language, heuristic]
            ax.text(i + j * 0.2 - 0.1, value + 0.001, f'{value:.5f}', ha='center', va='bottom', fontsize=9)  # Slight offset

    # Save bar chart
    plt.savefig(os.path.join(plots_dir, 'heuristic_comparison_bar_chart.png'))
    plt.close()
    
    
    # Scatterplot of execution time vs instance num
    random_sample_df = df.groupby('language').apply(lambda x: x.sample(n = 250, random_state=23)).reset_index(drop=True) # randomly sample 250 points
    seaborn.set()
    plt.figure(figsize=(10, 6))
    seaborn.scatterplot(data=random_sample_df, x='instance_num', y='time', hue='language')
    plt.yscale("log")
    plt.title("Execution Time vs. Instance Number (Log Scale)")
    plt.xlabel("Instance Number")
    plt.ylabel("Execution Time (Log Scale)")
    plt.legend(title="Language", loc='upper right')
    plt.grid(linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(plots_dir, 'exec_time_vs_instance_num_scatterplot.png'), dpi=300)
    plt.close()



    # Print summary statistics
    stats_summary = df.groupby("language").apply(
        lambda group: pd.Series({
            "mean": group["time"].mean(),
            "std": group["time"].std(),
            "min": group["time"].min(),
            "max": group["time"].max(),
            "count": group["time"].count()
        })
    ).reset_index()
    print("Calculating common statistics for the algorithm implementations...")
    print(stats_summary)
    print("\n\n")

    # Perform Levene test to check for variance equality
    levene_stat, levene_pvalue = levene(
        *[df[df['language'] == lang]['time'] for lang in df['language'].unique()]
    )
    print("Performing levene test and outputting p-value...\n")
    print(f"Levene p-value: {levene_pvalue}")

    # Perform Welch ANOVA (doesn't assume equal variance comapred to normal ANOVA)
    welch_result = welch_anova(dv='time', between='language', data=df)
    print("\n\nPerforming Welch ANOVA...")
    print(welch_result)

    # Post-hoc analysis using Pairwise_gameshowell
    gameshowell = pairwise_gameshowell(dv='time', between='language', data=df)
    print("\nPairwise Gameshowell Test Results:")
    gameshowell['reject'] = gameshowell['pval'] < 0.05
    print(gameshowell)
    
    
    
    # also performing normal ANOVA and Tukey HSD just for comparison
    anova_groups = stats.f_oneway(
        *[df[df['language'] == lang]['time'] for lang in df['language'].unique()]
    )
    print("\n\nPerforming normal ANOVA for comparison...")
    print(f"f-statistic: {anova_groups.statistic}")
    print(f"p-value: {anova_groups.pvalue:.10e}")

    tukey = pairwise_tukeyhsd(endog=df["time"], groups=df["language"], alpha=0.05)
    print("\nTukey's HSD Test Results:")
    print(tukey)
    
    
    # statistics for heuristics
    print("\nCalculating average executino time for different heuristics for every language...")
    for language in df['language'].unique():
        euclidean = df[(df['heuristic'] == 0) & (df['language'] == language)]['time']
        manhattan = df[(df['heuristic'] == 1) & (df['language'] == language)]['time']
        
        euclidean_mean = euclidean.mean()
        manhattan_mean = manhattan.mean()
        print(f"Language: {language}")
        print(f"    Average Time (Euclidean): {euclidean_mean:.5f}")
        print(f"    Average Time (Manhattan): {manhattan_mean:.5f}\n")
    
    
    print("\nPerforming Levene test for different heuristics for every language...")
    for language in df['language'].unique():
        euclidean = df[(df['heuristic'] == 0) & (df['language'] == language)]['time']
        manhattan = df[(df['heuristic'] == 1) & (df['language'] == language)]['time']
        
        levene_stat, levene_pvalue = stats.levene(euclidean, manhattan)
        print(f"Language: {language}")
        print(f"Levene's Test Statistic: {levene_stat:.4f}, P-Value: {levene_pvalue:.4f}\n")
        
        
    print("\nPerforming t-test for different heuristics for every language")
    for language in df['language'].unique():
        euclidean = df[(df['heuristic'] == 0) & (df['language'] == language)]['time']
        manhattan = df[(df['heuristic'] == 1) & (df['language'] == language)]['time']
        
        t_stat, p_value = stats.ttest_ind(euclidean, manhattan, equal_var=True)
        print(f"Language: {language}")
        print(f"T-Statistic: {t_stat:.4f}, P-Value: {p_value:.4f}\n")
        
        
    # is execution time affected by instance_num?
    # we perform linear regression to see the relationship of the them
    print("\n\nPerforming linear regression on execution time vs instance_num...")
    X = df['instance_num'].values.reshape(-1,1)
    y = df['time']
    model = LinearRegression()
    model.fit(X,y)
    
    print(f"Slope: {model.coef_[0]}")   # we get a really small slope, implying little to no relationship
    print(f"Intercept: {model.intercept_}")



    # we want to predict what language it is based on heuristics and execution time (machine learning)
    print("\n\nPerforming Machine Learning Techniques to predict language...")
    heuristics = df['heuristic'].values.reshape(-1,1)
    time = df['time'].values.reshape(-1,1)

    X = np.hstack((heuristics, time))
    y = df['language']
    
    X_train, X_valid, y_train, y_valid = train_test_split(X, y)
    
    models = {
    "Naive Bayes": make_pipeline(StandardScaler(), GaussianNB()),   # around 0.6
    "K-Nearest Neighbors": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=100, weights='uniform', p=2)),  # this gets around 0.80 - 0.83
    "Decision Tree": DecisionTreeClassifier(max_depth=10),  # this gets around 0.8
    "Random Forest": RandomForestClassifier(n_estimators=75, max_depth=10, max_features='sqrt') # this gets around 0.8
    }
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        accuracy = model.score(X_valid, y_valid)
        print(f"\n{name} Accuracy: {accuracy:.4f}")
        
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('in_directory', type=str)
    args = parser.parse_args()
    main(args.in_directory)

