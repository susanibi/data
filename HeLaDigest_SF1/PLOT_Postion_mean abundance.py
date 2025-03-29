import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import os

# --- Select files and folder ---
tk.Tk().withdraw()
file_path = filedialog.askopenfilename(title="Select the abundance Excel file", filetypes=[("Excel Files", "*.xlsx")])
save_path = filedialog.askdirectory(title="Select folder to save plots")

# --- Define sheets and labels including 5.5 ---
sheets_50pg = {
    "3p2_50pg_ACN": "3.2 ACN",
    "3p2_50pg_NoACN": "3.2 NoACN",
    "3p5_50pg_ACN": "3.5 ACN",
    "3p5_50pg_NoACN": "3.5 NoACN",
    "5p5_50pg_ACN": "5.5 ACN",
    "5p5_50pg_NoACN": "5.5 NoACN"
}
sheets_250pg = {
    "3p2_250pg_ACN": "3.2 ACN",
    "3p2_250pg_NoACN": "3.2 NoACN",
    "3p5_250pg_ACN": "3.5 ACN",
    "3p5_250pg_NoACN": "3.5 NoACN",
    "5p5_250pg_ACN": "5.5 ACN",
    "5p5_250pg_NoACN": "5.5 NoACN"
}

# --- Color palettes ---
colors_50pg = ["#a7c7bd", "#c0d9d2", "#b5d1e0", "#cde3ee", "#7ba6c9", "#bcd3e6"]
colors_250pg = ["#6d9b8f", "#7fa79d", "#7297ad", "#94b6c6", "#567ba0", "#9db6cc"]

# --- Bootstrap function ---
def bootstrap_ci(data, num_bootstrap=1000, ci=95):
    medians = [np.median(np.random.choice(data, size=len(data), replace=True)) for _ in range(num_bootstrap)]
    lower = np.percentile(medians, (100 - ci) / 2)
    upper = np.percentile(medians, 100 - (100 - ci) / 2)
    return np.median(data), lower, upper

# --- Load Excel ---
xls = pd.ExcelFile(file_path)

def process_data(sheet_dict):
    medians, ci_errors = [], []
    for sheet in sheet_dict:
        df = xls.parse(sheet).select_dtypes(include='number')
        values = df.values.flatten()
        values = values[~np.isnan(values)]
        median_val, lower_ci, upper_ci = bootstrap_ci(values)
        error = median_val - lower_ci
        medians.append(median_val)
        ci_errors.append(error)
    return medians, ci_errors

# Process both 50pg and 250pg
medians_50, ci_errors_50 = process_data(sheets_50pg)
medians_250, ci_errors_250 = process_data(sheets_250pg)
max_y_250 = max([m + e for m, e in zip(medians_250, ci_errors_250)]) * 1.1

# Plot positions and labels
bar_positions = [0, 0.5, 1.3, 1.8, 2.6, 3.1]
x_labels_grouped = ["3.2 ACN", "3.2 NoACN", "3.5 ACN", "3.5 NoACN", "5.5 ACN", "5.5 NoACN"]
bar_width = 0.5

# --- Plotting function ---
def plot_bar(filename, title, medians, errors, colors, y_max=None):
    plt.figure(figsize=(12, 6))
    plt.bar(bar_positions, medians, yerr=errors, capsize=5,
            color=colors, edgecolor='black', width=bar_width, linewidth=0.8)
    plt.xticks(bar_positions, x_labels_grouped, fontsize=16)
    plt.ylabel("Median Abundance (± 95% CI)", fontsize=16)
    plt.title(title, fontsize=16)
    if y_max:
        plt.ylim(top=y_max)
    plt.grid(False)
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, filename), dpi=300)
    plt.close()

# --- Create plots for 50pg and 250pg ---
plot_bar("peptide_abundance_50pg.png", "Peptide Abundance 50pg (Median ± 95% CI)", medians_50, ci_errors_50, colors_50pg)
plot_bar("peptide_abundance_250pg.png", "Peptide Abundance 250pg (Median ± 95% CI)", medians_250, ci_errors_250, colors_250pg, max_y_250)

print(f"✅ Plots saved to: {save_path}")
