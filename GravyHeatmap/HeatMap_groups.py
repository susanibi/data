import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog
import os
import re
from matplotlib.colors import SymLogNorm


# Function to load multiple files using Tkinter
def load_multiple_files():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(title="Select CSV Files", filetypes=[("CSV Files", "*.csv")])
    return file_paths


# Function to save files in the same location as the heatmap
def save_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(title="Save Heatmap As", defaultextension=".png",
                                             filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"),
                                                        ("PDF File", "*.pdf")])
    return file_path


# Function to detect and group replicates dynamically
def process_replicates(df):
    grouped_df = pd.DataFrame()
    replicate_groups = {}

    # Pattern 1: Captures F_10.1 - F_1.5, R_10.1 - R_1.5
    pattern1 = re.compile(r"(F_\d+|R_\d+)\.\d+")

    # Pattern 2: Captures F1_0.1 - F2_0.5, R1_0.1 - R2_0.5
    pattern2 = re.compile(r"(R1|R2|F1|F2)_0\.\d+")

    # Pattern 3: Captures Evo_1.1 - Evo_1.5, Plate_1.1 - Plate_1.3
    pattern3 = re.compile(r"(Evo|Plate|F1|F2|R1|R2)_\d+\.\d+")

    detected_matches = []  # Store detected group names for debugging

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

        detected_matches.append(parent_name)

        if parent_name not in replicate_groups:
            replicate_groups[parent_name] = []
        replicate_groups[parent_name].append(col)

    # Debugging: Print detected replicate groups
    print("Detected replicate groups:", detected_matches)

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
    df["GravyScore_bin"] = pd.cut(df.index, bins=bin_edges, labels=[f"{round(edge, 1)}" for edge in bin_edges[:-1]])
    dfs[i] = df.groupby("GravyScore_bin", observed=True).sum()

# Merge all datasets based on bins
df_merged = pd.concat(dfs, axis=1, sort=False)

# Debugging: Check columns before sorting
print("Columns in df_merged before sorting:", df_merged.columns.tolist())
print("df_merged shape before sorting:", df_merged.shape)

# Fill missing values with 0
df_merged.fillna(0, inplace=True)

# Drop extra bin column (if it appears)
df_merged.drop(columns=["GravyScore_bin"], inplace=True, errors="ignore")

# **Correct Sorting**
desired_order = ["Evo", "Plate", "F1", "F2"] + [f"F_{i}" for i in range(1, 11)] + ["R1", "R2"] + [f"R_{i}" for i in
                                                                                                  range(1, 11)]

# Keep only existing columns and reorder correctly
existing_columns = [col for col in desired_order if col in df_merged.columns]

if not existing_columns:  # Check if any valid columns remain
    print("Error: No valid replicate groups found in final dataset. Please check the input files.")
    exit()

df_merged = df_merged[existing_columns]  # Select and reorder columns

# Debugging: Ensure df_merged is not empty
print("Final df_merged shape:", df_merged.shape)
print("df_merged head:\n", df_merged.head())

if df_merged.empty:
    print("Error: No data available for heatmap plotting. The dataset is empty.")
    exit()

# Transpose for heatmap (optional)
df_merged = df_merged.T  # Swap axes if needed

# Get min/max values for color scaling
data_min, data_max = df_merged.min().min(), df_merged.max().max()

# Apply SymLogNorm to enhance small values while preserving large ones
norm = SymLogNorm(linthresh=1000, vmin=data_min, vmax=data_max)

# Use magma colormap
custom_cmap = "magma"

# Generate the heatmap
plt.figure(figsize=(20, 10))
ax = sns.heatmap(df_merged, cmap=custom_cmap, norm=norm, linewidths=0.5, linecolor='gray')

# Adjust labels
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)  # **Set Y-axis labels to horizontal**
plt.xlabel("GravyScore Bins")
plt.ylabel("Samples (Replicates Summed)")
plt.title("Group sum in Bins")

# Save the heatmap
save_path = save_file()
if save_path:
    plt.savefig(save_path, dpi=300)
    print(f"Heatmap saved to: {save_path}")

    # Save merged CSV in the same directory
    merged_csv_path = os.path.join(os.path.dirname(save_path), "merged_heatmap_data.csv")
    df_merged.to_csv(merged_csv_path)
    print(f"Merged CSV saved to: {merged_csv_path}")

# Show the heatmap
plt.show()
