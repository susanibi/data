# This script uses the "Output_Combined_Mean_Abundance_and_%PSM.xlsx" file as input.
# It creates two heatmaps from the 'Mean_Abundance' sheet:
# 1. Raw Mean Abundance
# 2. Log10(Mean Abundance + 1)
# Missing values are colored the same as abundance = 0.
# You'll be prompted to select the file via a file dialog.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import tkinter as tk
from tkinter import filedialog

# --- Select File ---
root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(title="Select your abundance Excel file")

# --- Select Output Folder ---
output_folder = filedialog.askdirectory(title="Select folder to save heatmaps")

# --- Load Data ---
df = pd.read_excel(file_path, sheet_name="Mean_Abundance")

# --- Parse QC and sample data ---
abundance_long = df.melt(id_vars="GRAVY_bin", var_name="Condition", value_name="Abundance")
abundance_long = abundance_long[abundance_long["Abundance"].notna()]
abundance_long = abundance_long[~abundance_long["Condition"].str.contains("SEM")]

# Extract sample metadata safely
def parse_meta(row):
    if row["Condition"] == "QC_Mean":
        return pd.Series({"Sample": "QC", "Load": "", "Extraction": "", "Label": "QC"})
    parts = row["Condition"].split("_")
    if len(parts) >= 4:
        label = f"{parts[0]}_{parts[1]}_{parts[2]}"
        return pd.Series({
            "Sample": parts[0],
            "Load": parts[1],
            "Extraction": parts[2],
            "Label": label
        })
    else:
        return pd.Series({"Sample": None, "Load": None, "Extraction": None, "Label": None})

# Apply metadata extraction and filter invalid rows
meta = abundance_long.apply(parse_meta, axis=1)
abundance_long = pd.concat([abundance_long, meta], axis=1)
abundance_long = abundance_long[abundance_long["Label"].notna()]


# Lower-bound GRAVY
abundance_long["GRAVY_Lower"] = abundance_long["GRAVY_bin"].str.extract(r"([-+]?[0-9]*\.?[0-9]+)").astype(float)

# Pivot to heatmap format
pivot = abundance_long.pivot_table(index="Label", columns="GRAVY_Lower", values="Abundance")

# Reorder rows: QC, 50pg_ACN, 50pg_NoACN, 250pg_ACN, 250pg_NoACN
def sort_key(label):
    if label == "QC":
        return (0, "")
    parts = label.split("_")
    load_order = 1 if parts[1] == "50pg" else 2
    ext_order = 0 if parts[2] == "ACN" else 1
    return (load_order * 2 + ext_order, label)

pivot = pivot.reindex(sorted(pivot.index, key=sort_key))
pivot = pivot[sorted(pivot.columns)]

# Masked array for NaNs
masked_raw = np.ma.masked_invalid(pivot.values)
masked_log = np.ma.masked_invalid(np.log10(pivot.values + 1))

# Use same color for NaN as zero
zero_color = cm.viridis(0)
custom_cmap = cm.viridis.copy()
custom_cmap.set_bad(color=zero_color)

# Plot function
def plot_heatmap(data, title, filename, cmap):
    xticks = np.arange(data.shape[1])
    xtick_labels = [f"{val:.2f}" if i % 5 == 0 else "" for i, val in enumerate(pivot.columns)]
    yticks = np.arange(len(pivot.index))

    plt.figure(figsize=(16, 8))
    plt.imshow(data, aspect="auto", cmap=cmap)
    plt.colorbar(label="Mean Abundance")
    plt.xticks(ticks=xticks, labels=xtick_labels, rotation=90)
    plt.yticks(ticks=yticks, labels=pivot.index)
    plt.title(title)
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(filename, dpi=200, bbox_inches="tight")
    plt.close()

    print("Shape of heatmap data:", data.shape)
    print("Saving to:", filename)

    print(f"Saved: {filename}")

# Plot and save
import os

raw_path = os.path.join(output_folder, "heatmap_raw_abundance.png")
log_path = os.path.join(output_folder, "heatmap_log_abundance.png")

plot_heatmap(masked_raw, "Mean Abundance", raw_path, custom_cmap)
plot_heatmap(masked_log, "Log10(Mean Abundance + 1)", log_path, custom_cmap)


root.destroy()

