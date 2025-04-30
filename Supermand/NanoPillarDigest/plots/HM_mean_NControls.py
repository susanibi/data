# file input: avg-replicas-P1_report.pr_matrix.tsv_processed-P2_report.pr_matrix.tsv_processed - merged.csv

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog
import re

# --------------------------
# File selection via Tkinter
# --------------------------
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="Select the peptide data CSV file")

# Load the CSV
df = pd.read_csv(file_path)

# --------------------------
# Prepare heatmap matrix
# --------------------------

# Bin GravyScore
df["GravyBin"] = pd.cut(df["GravyScore"], bins=20)

# Define sample/replicate columns (based on actual file)
rep_cols = [
    'F1_0', 'F2_0',
    'F_1', 'F_2', 'F_3', 'F_4', 'F_5', 'F_6', 'F_7', 'F_8', 'F_9', 'F_10',
    'R1_0', 'R2_0',
    'R_1', 'R_2', 'R_3', 'R_4', 'R_5', 'R_6', 'R_7', 'R_8', 'R_9', 'R_10'
]

# Make sure columns are numeric
df[rep_cols] = df[rep_cols].apply(pd.to_numeric, errors='coerce')

# Group by gravy bin and calculate mean abundance
heatmap_data = df.groupby("GravyBin", observed=False)[rep_cols].mean().T

# Format gravy bin labels (lower bounds, 2 decimals)
heatmap_data.columns = [f"{interval.left:.2f}" for interval in heatmap_data.columns]

# Define a custom sort key
def sort_key(label):
    if label == "F1_0":
        return (0, 0)
    elif label == "F2_0":
        return (0, 1)
    elif re.match(r"^F_\d+$", label):
        return (0, 10 + int(label.split('_')[1]))
    elif label == "R1_0":
        return (1, 0)
    elif label == "R2_0":
        return (1, 1)
    elif re.match(r"^R_\d+$", label):
        return (1, 10 + int(label.split('_')[1]))
    else:
        return (2, label)

# Apply custom order
sorted_labels = sorted(heatmap_data.index, key=sort_key)
heatmap_final = heatmap_data.loc[sorted_labels]

# --------------------------
# Plotting the heatmap
# --------------------------
plt.figure(figsize=(18, 10))
sns.heatmap(heatmap_final, cmap="viridis", linewidths=0, linecolor='gray')

plt.title("Peptide Abundance by Gravy Score Bin", fontsize=16)
plt.xlabel("Gravy Score (Lower bound)", fontsize=14)
plt.ylabel("", fontsize=14)
plt.yticks(fontsize=16)
plt.xticks(rotation=45, ha='center', fontsize=16)
plt.tight_layout()
plt.show()
