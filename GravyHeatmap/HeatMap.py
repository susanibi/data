import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog
import os
from matplotlib.colors import SymLogNorm

# -------------------------------
# 1. Tkinter helpers
# -------------------------------
def load_multiple_files():
    root = tk.Tk()
    root.withdraw()
    file_paths = filedialog.askopenfilenames(
        title="Select CSV Files",
        filetypes=[("CSV Files", "*.csv")]
    )
    return file_paths

def save_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title="Save Heatmap As",
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("PDF File", "*.pdf")]
    )
    return file_path

# -------------------------------
# 2. Load CSVs and convert index to numeric
# -------------------------------
file_paths = load_multiple_files()
if not file_paths:
    print("No files selected. Exiting.")
    exit()

dfs = []
for fp in file_paths:
    df = pd.read_csv(fp, index_col=0)
    df.index = pd.to_numeric(df.index, errors="coerce")
    df.sort_index(inplace=True)
    dfs.append(df)

# -------------------------------
# 3. Global binning (min/max across all CSVs)
# -------------------------------
global_min = min(df.index.min() for df in dfs)
global_max = max(df.index.max() for df in dfs)

num_bins = 50  # Adjust as needed
bin_edges = np.linspace(global_min, global_max, num_bins + 1)
bin_labels = [f"{round(edge, 1)}" for edge in bin_edges[:-1]]

# -------------------------------
# 4. Bin each DataFrame & aggregate (keep all numeric columns)
# -------------------------------
binned_dfs = []
for df in dfs:
    df["GravyScore_bin"] = pd.cut(
        df.index, bins=bin_edges, labels=bin_labels, include_lowest=True
    )
    # Group by bin and average all numeric columns
    df_grouped = df.groupby("GravyScore_bin", observed=True).sum(numeric_only=True)
    binned_dfs.append(df_grouped)

# -------------------------------
# 5. Merge all binned DataFrames (concatenate on columns)
# -------------------------------
df_merged = pd.concat(binned_dfs, axis=1, sort=False)
df_merged.fillna(0, inplace=True)
df_merged.drop(columns=["GravyScore_bin"], inplace=True, errors="ignore")

# -------------------------------
# 6. Transpose so that rows = original column names
# -------------------------------
df_merged = df_merged.T

# -------------------------------
# 7. Custom sort function
# -------------------------------
def parse_sample_name(name):
    """
    Parse sample names and assign group order:
      - Evo: group 0
      - Plate: group 1
      - F1: group 2
      - F2: group 3
      - F_y.x (starts with "F_"): group 4
      - R1: group 5
      - R2: group 6
      - R_y.x (starts with "R_"): group 7
      - Others: group 8
    Then, within the group, sort by the numeric parts.
    """
    # Default values
    group_order = 8
    main_num = 0
    sub_num = 0

    if name.startswith("Evo"):
        group_order = 0
    elif name.startswith("Plate"):
        group_order = 1
    elif name.startswith("F1"):
        group_order = 2
    elif name.startswith("F2"):
        group_order = 3
    elif name.startswith("F_"):
        group_order = 4
    elif name.startswith("R1"):
        group_order = 5
    elif name.startswith("R2"):
        group_order = 6
    elif name.startswith("R_"):
        group_order = 7

    # Try to extract numeric parts after the underscore.
    try:
        parts = name.split("_", 1)[1]
        # parts expected as "0.x" or "y.x" etc.
        main_str, sub_str = parts.split(".")
        main_num = int(main_str)
        sub_num = int(sub_str)
    except Exception:
        main_num, sub_num = 0, 0

    return (group_order, main_num, sub_num)

sorted_rows = sorted(df_merged.index, key=parse_sample_name)
df_merged = df_merged.reindex(sorted_rows)

# -------------------------------
# 8. Setup color scaling for heatmap
# -------------------------------
data_min, data_max = df_merged.min().min(), df_merged.max().max()
if data_min == data_max:
    norm = None
else:
    norm = SymLogNorm(linthresh=1000, vmin=data_min, vmax=data_max)
custom_cmap = "magma"  # Try alternatives like "viridis" or "YlOrRd"

# -------------------------------
# 9. Plot the heatmap
# -------------------------------
plt.figure(figsize=(20, 10))
sns.heatmap(
    df_merged,
    cmap=custom_cmap,
    norm=norm,
    linewidths=0.5,
    linecolor='gray'
)
plt.xticks(rotation=45, ha="right")
plt.xlabel("GravyScore Bins")
plt.ylabel("Samples")
plt.title("Heatmap with Global Binning and Custom Sorted Samples")

# -------------------------------
# 10. Save the heatmap and merged CSV
# -------------------------------
save_path = save_file()
if save_path:
    plt.savefig(save_path, dpi=300)
    print(f"Heatmap saved to: {save_path}")
    merged_csv_path = os.path.join(os.path.dirname(save_path), "merged_heatmap_data.csv")
    df_merged.to_csv(merged_csv_path)
    print(f"Merged CSV saved to: {merged_csv_path}")

plt.show()
