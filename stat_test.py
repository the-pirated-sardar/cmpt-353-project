import pandas as pd
import scipy.stats as stats
import argparse
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from sklearn.preprocessing import StandardScaler
from scipy.stats import levene

def main(in_directory):
  
  df = pd.read_csv(in_directory)
  
  df = df[df['time'] > 0.0]
  
  # Step 1: Handle heuristic == 0
  df_heuristic_0 = df[df['heuristic'] == 0]

  # Pivot the data for heuristic == 0
  df_heuristic_0_pivot = df_heuristic_0.pivot(index='instance_num', columns='language', values='time')
  df_heuristic_0_pivot = df_heuristic_0_pivot.dropna()

  # Fit the LOF model for anomaly detection on heuristic == 0
  model_0 = LocalOutlierFactor(n_neighbors=20)
  y_heuristic_0 = model_0.fit_predict(df_heuristic_0_pivot.values)
  df_heuristic_0_pivot['lof_outlier'] = y_heuristic_0

  # Filter out outliers for heuristic == 0
  df_heuristic_0_inliers = df_heuristic_0_pivot[df_heuristic_0_pivot['lof_outlier'] == 1]

  # Step 2: Handle heuristic == 1
  df_heuristic_1 = df[df['heuristic'] == 1]

  # Pivot the data for heuristic == 1
  df_heuristic_1_pivot = df_heuristic_1.pivot(index='instance_num', columns='language', values='time')
  df_heuristic_1_pivot = df_heuristic_1_pivot.dropna()

  # Fit the LOF model for anomaly detection on heuristic == 1
  model_1 = LocalOutlierFactor(n_neighbors=20)
  y_heuristic_1 = model_1.fit_predict(df_heuristic_1_pivot.values)
  df_heuristic_1_pivot['lof_outlier'] = y_heuristic_1

  # Filter out outliers for heuristic == 1
  df_heuristic_1_inliers = df_heuristic_1_pivot[df_heuristic_1_pivot['lof_outlier'] == 1]

  # Step 3: Combine the results
  df_cleaned = pd.concat([df_heuristic_0_inliers, df_heuristic_1_inliers])
  df_unpivoted = df_cleaned.reset_index().melt(id_vars=['instance_num'], value_vars=df_cleaned.columns[:-1], var_name='language', value_name='time')
  df = df_unpivoted.merge(df[['instance_num', 'heuristic']].drop_duplicates(), on='instance_num', how='left')

  #Just useful for debugging
  #outliers = df_heuristic_0_pivot[df_heuristic_0_pivot['lof_outlier'] == -1]
  #print(f"Detected outliers: \n{outliers}")
  #outliers = df_heuristic_1_pivot[df_heuristic_1_pivot['lof_outlier'] == -1]
  #print(f"Detected outliers: \n{outliers}")
  
  
  # outputting a histogram of time for every language
  languages = df['language'].unique()
  figure, axes = plt.subplots(1, len(languages), figsize=(15, 6))
  
  axes[0].hist(df[df['language'] == 'C++']['time'], bins=25, color='blue', edgecolor='grey', alpha=0.7)
  axes[0].set_title('C++')
  axes[0].set_xlabel('Execution Time')
  axes[0].set_ylabel('Frequency')
  
  axes[1].hist(df[df['language'] == 'Java']['time'], bins=25, color='red', edgecolor='grey', alpha=0.7)
  axes[1].set_title('Java')
  axes[1].set_xlabel('Execution Time')
  axes[1].set_ylabel('Frequency')
  
  axes[2].hist(df[df['language'] == 'JavaScript']['time'], bins=25, color='green', edgecolor='grey', alpha=0.7)
  axes[2].set_title('JavaScript')
  axes[2].set_xlabel('Execution Time')
  axes[2].set_ylabel('Frequency')

  axes[3].hist(df[df['language'] == 'Python']['time'], bins=25, color='grey', edgecolor='grey', alpha=0.7)
  axes[3].set_title('Python')
  axes[3].set_xlabel('Execution Time')
  axes[3].set_ylabel('Frequency')
  
  #plt.show()
  plt.savefig('histograms.png')
  
  
  # print a general summary of the stats
  stats_summary = df.groupby("language").apply(
    lambda group: pd.Series({
      "mean": group["time"].mean(),
      "std": group["time"].std()
    })
  ).reset_index()
  print("Calculating the means and standard deviation of the algorithm implementation...")
  print(stats_summary)
  print("\n\n")
  
  
  # perform levene test to see if we can do ANOVA
  levene_stat, levene_pvalue = levene(
    df[df['language'] == 'C++']['time'],
    df[df['language'] == 'Java']['time'],
    df[df['language'] == 'JavaScript']['time'],
    df[df['language'] == 'Python']['time']
  )
  print(f"Levene p-value: {levene_pvalue}")
  
  
  
  # perform welsch ANOVA, which is more robust to uneven variance
  c_plus_plus = df[df['language'] == 'C++']['time']
  java = df[df['language'] == 'Java']['time']
  javascript = df[df['language'] == 'JavaScript']['time']
  python = df[df['language'] == 'Python']['time']  

  anova_groups = stats.f_oneway(c_plus_plus, java, javascript, python)
  
  print("\n\nPerforming ANOVA...")
  print(f"f-statistic: {anova_groups.statistic}")
  print(f"p-value: {anova_groups.pvalue:.10e}")
  
  
  # post-hoc
  tukey = pairwise_tukeyhsd(endog=df["time"], groups=df["language"], alpha=0.05)
  print("\nTukey's HSD Test Results:")
  print(tukey)
  
  
  
  
  
  
  


  
  
  
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('in_directory', type=str)
  args = parser.parse_args()
  main(args.in_directory)