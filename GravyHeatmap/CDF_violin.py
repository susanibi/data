import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog
import os
import re
from scipy.stats import mannwhitneyu


# Function to load multiple files using Tkinter
def load_multiple_files():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Select CSV Files", filetypes=[("CSV Files", "*.csv")])
    return file_paths


# Function to save image files (CDF & violin plot)
def save_image_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title="Save Image File As",
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("PDF File", "*.pdf")]
    )
    return file_path


# Function to save CSV files
def save_csv_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title="Save CSV File As",
        defaultextension=".csv",
        filetypes=[("CSV File", "*.csv")]
    )
    return file_path


# Function to detect and group replicates dynamically
def process_replicates(df):
    grouped_df = pd.DataFrame()
    replicate_groups = {}

    # Pattern 1: Captures F_10.1 - F_1.5, R_10.1 - R_1.5
    pattern1 = re.compile(r"(F_\d+|R_\d+)\.\d+")

    # Pattern 2: Captures R1_0.1 - R1_0.5, R2_0.1 - R2_0.5, F1_0.1, F2_0.5
    pattern2 = re.compile(r"(R1|R2|F1|F2)_0\.\d+")

    # Pattern 3: Captures Evo_1.1 - Evo_1.5, Plate_1.1 - Plate_1.3
    pattern3 = re.compile(r"(Evo|Plate|F1|F2|R1|R2)_\d+\.\d+")

    for col in df.columns:
        match1 = pattern1.match(col)
        match2 = pattern2.match(col)
        match3 = pattern3.match(col)

        if match1:
            parent_name = match1.group(1)
        elif match2:
            parent_name = match2.group(1)
        elif match3:
            parent_name = match3.group(1)
        else:
            continue  # Skip columns that don't match

        if parent_name not in replicate_groups:
            replicate_groups[parent_name] = []
        replicate_groups[parent_name].append(col)

    # Sum replicates for each group and store in the new DataFrame
    for parent_name, columns in replicate_groups.items():
        grouped_df[parent_name] = df[columns].sum(axis=1)

    return grouped_df


# Load multiple datasets
file_paths = load_multiple_files()
if not file_paths:
    print("No files selected. Exiting.")
    exit()

# Load all datasets and process replicates
dfs = []
for file in file_paths:
    df = pd.read_csv(file, index_col=0)
    df.index = pd.to_numeric(df.index, errors="coerce")  # Ensure numeric GravyScore bins
    df.sort_index(inplace=True)  # Sort for consistency
    df_processed = process_replicates(df)  # Apply replicate summing
    dfs.append(df_processed)

# Find global min & max across all datasets
global_min = min(df.index.min() for df in dfs)
global_max = max(df.index.max() for df in dfs)

# Define bins that work for all datasets
num_bins = 50  # Adjust bin size if needed
bin_edges = np.linspace(global_min, global_max, num_bins + 1)

# Apply binning to all datasets
for i, df in enumerate(dfs):
    df["GravyScore_bin"] = pd.cut(df.index, bins=bin_edges, labels=[f"{round(edge, 2)}" for edge in bin_edges[:-1]],
                                  include_lowest=True)
    dfs[i] = df.groupby("GravyScore_bin", observed=True).sum()

# Merge datasets after binning
df_merged = pd.concat(dfs, axis=1, sort=False)

# Ensure GravyScore_bin is an index
df_merged.index.name = "GravyScore"

# Transpose to match expected format for plotting
df_melted = df_merged.reset_index().melt(id_vars="GravyScore", var_name="Group", value_name="GravyScore_Value")

# Print descriptive statistics to check if groups are different
print(df_melted.groupby("Group")["GravyScore_Value"].describe())

# **PLOT 1: CDF - Cumulative Distribution Function**
plt.figure(figsize=(10, 6))

# Plot CDF for each group
for group in df_melted["Group"].unique():
    sorted_values = np.sort(df_melted[df_melted["Group"] == group]["GravyScore_Value"])
    cdf = np.arange(1, len(sorted_values) + 1) / len(sorted_values)
    plt.plot(sorted_values, cdf, label=group)

# Customize CDF plot
plt.xlabel("GravyScore")
plt.ylabel("Cumulative Probability")
plt.title("Cumulative Distribution Function (CDF) of GravyScores")
plt.legend(loc="best")
plt.grid()

# Save CDF Plot
save_path = save_image_file()
if save_path:
    plt.savefig(save_path, dpi=300)
    print(f"CDF plot saved to: {save_path}")

plt.show()

# **PLOT 2: Violin Plot of GravyScore Distributions**
plt.figure(figsize=(12, 6))
sns.violinplot(x="Group", y="GravyScore_Value", data=df_melted, inner="quartile", density_norm="width")

# Customize Violin Plot
plt.xticks(rotation=45, ha="right")
plt.xlabel("Sample Groups")
plt.ylabel("GravyScore")
plt.title("Violin Plot of GravyScore Distributions")

# Save Violin Plot
save_path = save_image_file()
if save_path:
    plt.savefig(save_path, dpi=300)
    print(f"Violin plot saved to: {save_path}")

plt.show()

# **Mann-Whitney U Test for Statistical Difference**
evo_scores = pd.to_numeric(df_melted[df_melted["Group"] == "Evo"]["GravyScore_Value"], errors="coerce").dropna()

results = []
for group in df_melted["Group"].unique():
    if group == "Evo":
        continue

    group_scores = pd.to_numeric(df_melted[df_melted["Group"] == group]["GravyScore_Value"], errors="coerce").dropna()

    if len(evo_scores) > 0 and len(group_scores) > 0:
        stat, p_value = mannwhitneyu(evo_scores, group_scores, alternative="two-sided")
        results.append({"Group": group, "Mann-Whitney U": stat, "p-value": p_value})
    else:
        print(f"Skipping Mann-Whitney U test for {group} due to insufficient data.")

# Convert results to DataFrame and save
results_df = pd.DataFrame(results)
results_csv_path = save_csv_file()
if results_csv_path:
    if not results_csv_path.endswith(".csv"):
        results_csv_path += ".csv"
    results_df.to_csv(results_csv_path, index=False)
    print(f"Statistical test results saved to: {results_csv_path}")
