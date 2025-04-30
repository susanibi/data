
#!/usr/bin/env python3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import re

# Custom font size settings
XTICK_FONT_SIZE = 16
YTICK_FONT_SIZE = 16
AXIS_LABEL_FONT_SIZE = 20
TITLE_FONT_SIZE = 16

def main():
    # --- File dialog to select input CSV ---
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select the GRAVY-binned missingness CSV",
        filetypes=[("CSV files", "*.csv")]
    )

    if not file_path:
        print("No file selected. Exiting.")
        return

    # --- Load the data ---
    df = pd.read_csv(file_path)

    # --- Convert GRAVY bin to midpoint for plotting ---
    df['GravyMid'] = df['GravyBin'].apply(
        lambda x: (pd.Interval(float(x.split(',')[0][1:]), float(x.split(',')[1][:-1]), closed='right').left +
                   pd.Interval(float(x.split(',')[0][1:]), float(x.split(',')[1][:-1]), closed='right').right) / 2
        if isinstance(x, str) and ',' in x else None
    )

    # --- Melt for long-form plotting ---
    df_long = df.melt(id_vars=['GravyBin', 'GravyMid'], var_name='Sample', value_name='Missingness')
    heatmap_data = df_long.pivot(index='Sample', columns='GravyMid', values='Missingness')

    # --- Apply custom sample order ---
    custom_order = []
    custom_order += sorted([s for s in heatmap_data.index if s.startswith("Evo")])
    custom_order += sorted([s for s in heatmap_data.index if s.startswith("Plate")])
    custom_order += sorted([s for s in heatmap_data.index if s == "F1"])
    custom_order += sorted([s for s in heatmap_data.index if s == "F2"])
    custom_order += sorted([s for s in heatmap_data.index if re.match(r"F_\d+", s)], key=lambda x: int(x.split("_")[1]))
    custom_order += sorted([s for s in heatmap_data.index if s == "R1"])
    custom_order += sorted([s for s in heatmap_data.index if s == "R2"])
    custom_order += sorted([s for s in heatmap_data.index if re.match(r"R_\d+", s)], key=lambda x: int(x.split("_")[1]))

    # --- Filter to valid samples only and reorder ---
    heatmap_ordered = heatmap_data.loc[[s for s in custom_order if s in heatmap_data.index]]

    # --- Plot the heatmap ---
    plt.figure(figsize=(14, 10))
    ax = sns.heatmap(
        heatmap_ordered,
        cmap='magma',
        cbar_kws={'label': 'Missingness'},
        xticklabels=True,
        yticklabels=True
    )

    # ✅ Get the actual colorbar object from the heatmap
    colorbar = ax.collections[0].colorbar

    # ✅ Set colorbar tick and label font sizes
    colorbar.set_label('Missingness', fontsize=16)
    colorbar.ax.tick_params(labelsize=14, length=0)

    # Format x-tick labels to 2 decimal places
    x_labels = ["{:.2f}".format(float(label.get_text())) for label in ax.get_xticklabels()]
    ax.set_xticklabels(x_labels, fontsize=XTICK_FONT_SIZE, rotation=45)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=YTICK_FONT_SIZE)

    # Axis labels and title
    ax.set_xlabel('GRAVY Score (Bin Midpoint)', fontsize=AXIS_LABEL_FONT_SIZE)
    ax.set_ylabel('', fontsize=AXIS_LABEL_FONT_SIZE)
    ax.set_title('Non-Detection Frequency', fontsize=TITLE_FONT_SIZE)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
