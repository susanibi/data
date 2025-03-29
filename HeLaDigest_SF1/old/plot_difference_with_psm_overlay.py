# This script uses:
#   - Abundance_Comparison_3p2_vs_3p5_updated.csv (with mean, SEM, difference)
#   - COMBINED_abundance_PSM_ALL_new.xlsx (to get %PSM per bin)
#
# It creates a GRAVY vs Abundance Difference plot (3p2 - 3p5)
# with SEM shading, GRAVY-colored dots, and a subtle %PSM overlay.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colormaps
from tkinter import filedialog, Tk

def main():
    # File selection
    root = Tk()
    root.withdraw()

    diff_csv = filedialog.askopenfilename(title="Select Abundance_Comparison_3p2_vs_3p5_updated.csv")
    psm_excel = filedialog.askopenfilename(title="Select COMBINED_abundance_PSM_ALL_new.xlsx")

    if not diff_csv or not psm_excel:
        print("❌ File selection canceled.")
        return

    # Load abundance comparison
    df = pd.read_csv(diff_csv)
    gravy_bin = df["GRAVY_bin"].astype(float).to_numpy()
    diff = df["Difference"].astype(float).to_numpy()
    sem0 = df["Combined_SEM0"].astype(float).to_numpy()

    # Load %PSM data from Excel
    psm_df = pd.read_excel(psm_excel, sheet_name="ALL_%PSM_Individual")
    psm_subset = psm_df[["GRAVY_bin_LB", "3p2_50pg_ACN", "3p5_50pg_ACN"]].dropna()
    psm_subset.columns = ["GRAVY_bin", "3p2_PSM", "3p5_PSM"]

    # Merge
    merged = pd.merge(df, psm_subset, left_on="GRAVY_bin", right_on="GRAVY_bin")
    psm_3p2 = merged["3p2_PSM"].astype(float).to_numpy()
    psm_3p5 = merged["3p5_PSM"].astype(float).to_numpy()

    # Color mapping by GRAVY
    cmap = colormaps["viridis"]
    norm = plt.Normalize(gravy_bin.min(), gravy_bin.max())
    colors = cmap(norm(gravy_bin))

    # Plot
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot difference
    for xi, yi, ci in zip(gravy_bin, diff, colors):
        ax1.plot(xi, yi, marker='o', color=ci)
    ax1.plot(gravy_bin, diff, color='gray', alpha=0.5)
    ax1.fill_between(gravy_bin, diff - sem0, diff + sem0, color='lightgray', alpha=0.3)
    ax1.axhline(0, color='gray', linestyle='--')

    ax1.set_ylabel("Abundance Difference (3p2 - 3p5)")
    ax1.set_xlabel("GRAVY Bin Lower Bound")
    ax1.set_title("Abundance Difference (3p2 - 3p5) with %PSM Overlay")
    ax1.grid(True)

    # GRAVY colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax1, label="GRAVY Hydropathy")

    # Overlay %PSM as soft background bars
    ax2 = ax1.twinx()
    bar_width = 0.005

    for xi, h in zip(gravy_bin, psm_3p2):
        ax2.bar(xi - bar_width, h, width=bar_width*3, color='cornflowerblue', alpha=0.38, zorder=0)
    for xi, h in zip(gravy_bin, psm_3p5):
        ax2.bar(xi + bar_width, h, width=bar_width*3, color='mediumseagreen', alpha=0.38, zorder=0)

    ax2.set_ylabel("% PSM (Per Bin)")
    ax2.tick_params(axis='y', colors='gray')

    # Legend
    custom_lines = [
        plt.Line2D([0], [0], color='gray', lw=2, label="3p2 - 3p5 Difference"),
    ]
    ax1.legend(handles=custom_lines, loc="upper left")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
