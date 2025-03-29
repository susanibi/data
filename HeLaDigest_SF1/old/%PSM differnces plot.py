"""
This script compares %PSM distributions between 3p2 and 3p5 (ACN, 50pg) surfaces,
using the 'COMBINED_abundance_PSM_ALL_new.xlsx' file as input.

It calculates the difference in %PSM for each GRAVY bin, and creates a
flat 2D bar plot colored by GRAVY hydropathy (viridis gradient).
Neutral hydropathy bins (-1 ≤ GRAVY ≤ 1) are shown in gray.

Required:
- Sheet name: ALL_%PSM_Individual
- Columns needed: GRAVY_bin_LB, 3p2_50pg_ACN, 3p5_50pg_ACN
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

# Load file
file_path = "COMBINED_abundance_PSM_ALL_new.xlsx"
df = pd.read_excel(file_path, sheet_name="ALL_%PSM_Individual")

# Keep relevant columns and drop missing
df = df[["GRAVY_bin_LB", "3p2_50pg_ACN", "3p5_50pg_ACN"]].dropna()

# Calculate difference and assign hydropathy category
df["Difference"] = df["3p2_50pg_ACN"] - df["3p5_50pg_ACN"]

def gravy_category(g):
    if g < -1:
        return "Hydrophilic"
    elif g > 1:
        return "Hydrophobic"
    else:
        return "Neutral"

df["GRAVY_Category"] = df["GRAVY_bin_LB"].apply(gravy_category)

# Normalize GRAVY values for viridis color scale
norm = mcolors.Normalize(df["GRAVY_bin_LB"].min(), df["GRAVY_bin_LB"].max())
cmap = cm.get_cmap("viridis")

# Assign bar colors
df["Color"] = [
    "lightgray" if cat == "Neutral" else cmap(norm(gravy))
    for gravy, cat in zip(df["GRAVY_bin_LB"], df["GRAVY_Category"])
]

# Plot
fig, ax = plt.subplots(figsize=(12, 6))
bar_width = 0.05

ax.bar(
    df["GRAVY_bin_LB"],
    df["Difference"],
    width=bar_width,
    color=df["Color"],
    linewidth=0
)

# Add colorbar
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax)
cbar.set_label("GRAVY Bin (Hydropathy)", fontsize=12)
cbar.ax.tick_params(labelsize=10)

# Axis labels and styling
ax.axhline(0, linestyle="--", color="black")
ax.set_title("%PSM Difference per GRAVY Bin (3p2 - 3p5)", fontsize=14)
ax.set_xlabel("GRAVY Bin (Lower Bound)", fontsize=12)
ax.set_ylabel("Δ %PSM (3p2 - 3p5)", fontsize=12)
ax.set_xticks(df["GRAVY_bin_LB"][::5])
ax.tick_params(axis='x', rotation=90, labelsize=10)
ax.tick_params(axis='y', labelsize=10)

plt.tight_layout()
plt.show()
