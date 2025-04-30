import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import sem
from matplotlib.patches import Rectangle

# === Peptide Data ===
data = pd.DataFrame({
    "Sample": [
        "B6", "B7", "B8", "A8", "B2", "A2", "A12", "B5",
        "A7", "A3", "A9", "A11", "B3", "B4", "A5",
        "A6", "A1", "A10", "A4", "B1"
    ],
    "%F68": ["0", "0", "0", "0", "0", "0.03", "0.05", "0.05",
             "0", "0.03", "0.03", "0.03", "0.03", "0.03", "0.05",
             "0", "0", "0.03", "0.05", "0.05"],
    "HeLa (pg)": [0, 0, 0, 50, 50, 50, 50, 50,
                  125, 125, 125, 125, 125, 125, 125,
                  200, 200, 200, 200, 200],
    "Peptides": [505, 445, 204, 3812, 3465, 5732, 4615, 4746,
                 7604, 8396, 7861, 7308, 7765, 7197, 7885,
                 8558, 8554, 8317, 8253, 6564]
})

# === Evotest-Control Data ===
Control = pd.DataFrame({
    "HeLa (pg)": [125, 125, 125],
    "%F68": ["Control"] * 3,
    "Peptides": [8958, 8994, 7827]
})

# Combine and summarize
full_data = pd.concat([data[["HeLa (pg)", "%F68", "Peptides"]], Control])
summary = full_data.groupby(["HeLa (pg)", "%F68"]).agg(
    Avg=("Peptides", "mean"),
    SEM=("Peptides", sem),
    Replicates=("Peptides", "count")
).reset_index()

# === Plot Config ===
hela_levels = sorted(summary["HeLa (pg)"].unique())
f68_order = ["0", "0.03", "0.05", "Control"]
bar_width = 0.18
x_positions = [0, 0.6, 1.6, 2.6]  # Custom x positions


# 🎨 Final refined blue-green palette
base_colors = {
    "0": "#b4dcec",        # Soft Sky
    "0.03": "#457b9d",     # Ocean Blue
    "0.05": "#264653",     # Deep Navy Ocean
    "Control": "#d9d9d9"   # Pale Gray
}



# === Plotting ===
fig, ax = plt.subplots(figsize=(10, 6))

for i, hela in enumerate(hela_levels):
    subset = summary[summary["HeLa (pg)"] == hela]
    present_f68 = [f for f in f68_order if f in subset["%F68"].values]
    n = len(present_f68)
    offsets = np.linspace(-bar_width * (n - 1) / 2, bar_width * (n - 1) / 2, n)

    for offset, f68 in zip(offsets, present_f68):
        row = subset[subset["%F68"] == f68].iloc[0]
        xpos = x_positions[i] + offset
        color = base_colors[f68]
        ax.bar(xpos, row.Avg, width=bar_width, yerr=row.SEM, capsize=5,
               color=color, edgecolor='black', linewidth=0.4)
        ax.text(xpos, 5, f"n={int(row.Replicates)}", ha='center', va='bottom',
                color='white', fontsize=11)

# === Axes and Labels ===
ax.set_xticks(x_positions)
ax.set_xticklabels(hela_levels, fontsize=14)                # Tick label font size
ax.set_xlabel("Initial load of HeLa Digest (pg)", fontsize=14, labelpad=10)        # X-axis label + font size
ax.set_ylabel("Peptide IDs", fontsize=14, labelpad=10)   # Y-axis label + font size
ax.set_title("\n", fontsize=16)     # Title font size
ax.tick_params(axis='both', which='major', labelsize=12)    # General tick font size



# === Legend ===
legend_handles = [
    Rectangle((0, 0), 1, 1, color=base_colors[f], label=f"%F68 = {f}")
    for f in ["0", "0.03", "0.05"]
]
legend_handles.append(Rectangle((0, 0), 1, 1, color=base_colors["Control"], label="Control"))
ax.legend(handles=legend_handles, title="%F68", loc="upper left")

# Optional: legend font size
ax.legend(handles=legend_handles, title="", loc="upper left", fontsize=11, title_fontsize=12)

# === Grid & Style ===
ax.grid(axis='y', color="#dddddd", linestyle="--")
ax.set_axisbelow(True)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
for spine in ["left", "bottom"]:
    ax.spines[spine].set_color("#888888")
    ax.spines[spine].set_linewidth(1)

plt.tight_layout()
plt.show()
