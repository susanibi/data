import matplotlib.pyplot as plt

# Categories and surfaces (with manual newlines for wrapping)
categories = ['CA',
              'Dispensing\nEfficiency',
              '% Deviation\nfrom R/F_5',
              'Hydrophilic-\nDetection',
              'Hydrophobic-\nDetection',
              'Number of\nDiff. Peptides',
              '% Recover\nof Evo']

surfaces = ['F (1→10)', 'R (1→10)']

# Trend data: (arrow, color)
trend_data = [
    [('↑', 'lightgreen'), ('↓', 'lightcoral'), ('→', 'grey'), ('↑', 'lightgreen'), ('↑', 'lightgreen'), ('↑', 'lightgreen'), ('→', 'grey')],
    [('→', 'grey'), ('↓', 'lightcoral'), ('↑', 'lightgreen'), ('↑', 'lightgreen'), ('↑↑', 'darkgreen'), ('↑', 'lightgreen'), ('↑', 'lightgreen')]
]

# Font sizes
arrow_fontsize = 46
category_fontsize = 26
surface_fontsize = 26

# Create plot
fig, ax = plt.subplots(figsize=(22, 7))
ax.axis('off')

# Plot arrows
for row_idx, surface in enumerate(surfaces):
    for col_idx, category in enumerate(categories):
        arrow, color = trend_data[row_idx][col_idx]
        ax.text(col_idx + 0.5, len(surfaces) - row_idx - 0.5, arrow, ha='center', va='center', fontsize=arrow_fontsize, fontweight='bold', color=color)

# Plot category headers
for col_idx, category in enumerate(categories):
    ax.text(col_idx + 0.5, len(surfaces) + 0.5, category, ha='center', va='bottom', fontsize=category_fontsize, weight='bold')

# Plot surface labels
for row_idx, surface in enumerate(surfaces):
    ax.text(-0.5, len(surfaces) - row_idx - 0.5, surface, ha='right', va='center', fontsize=surface_fontsize, weight='bold')

# Adjust plot limits
ax.set_xlim(-0.5, len(categories))
ax.set_ylim(0, len(surfaces) + 1.5)

plt.tight_layout()
plt.show()
