import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define weight ratio from model (unused in this script snippet but left for context)
weight_ratio = 5.24

# Hardcoded data
data = pd.DataFrame({
    "Cell Type": ["HEK", "HeLa", "HEK", "HEK", "HEK", "Mouse BM", "AML"],
    "Conc Group": ["≤40", "≤40", "300", "300", "300", "300", "300"],
    "Split Eff": [100, 100, 90.63, 78.13, 93.36, 100, 96.89]
})

# Group and compute mean and std dev
grouped = data.groupby(["Cell Type", "Conc Group"]).agg(
    mean_eff=("Split Eff", "mean"),
    std_eff=("Split Eff", "std")
).reset_index()

# Create labels and positions with spacing
grouped["Group Label"] = grouped["Cell Type"] + " (" + grouped["Conc Group"] + ")"
order = ["HEK (≤40)", "HeLa (≤40)", "HEK (300)", "Mouse BM (300)", "AML (300)"]
grouped = grouped[grouped["Group Label"].isin(order)]
grouped["Group Label"] = pd.Categorical(grouped["Group Label"], categories=order, ordered=True)
grouped = grouped.sort_values("Group Label")

# Manual x positions to introduce a gap between groups
positions = [0, 1, 3, 4, 5]
tick_labels = ["HEK", "HeLa", "HEK", "Mouse BM", "AML"]

custom_colors = {
    "HEK (≤40)": "#264653",          # Dark navy
    "HEK (300)": "#264653",          # Dark navy (same as for HEK (≤40))
    "HeLa (≤40)": "#7093B6",         # Soft turquoise with a hint of purple
    "Mouse BM (300)": "#66A3C2",      # Soft pastel green
    "AML (300)": "#748D8E"           # Soft pastel green
}
bar_colors = grouped["Group Label"].map(custom_colors).tolist()


# Plot setup
plt.figure(figsize=(10, 6))
bars = plt.bar(
    x=positions,
    height=grouped["mean_eff"],
    width=0.50,
    tick_label=tick_labels,
    yerr=grouped["std_eff"],
    color=bar_colors,
    edgecolor="black",
    capsize=5,
    zorder=3 # Ensure bars are drawn on top
)

plt.title("", fontsize=13)
plt.ylabel("Average Split Efficiency (%)", fontsize=14)
plt.ylim(0, 110)

# Make the grid lines light grey (and position them behind the bars)
plt.grid(axis="y", color="lightgrey", linestyle="--", zorder=0)

# Add a horizontal reference line at y=100 in light grey behind the bars
plt.axhline(y=100, color="lightgrey", linewidth=2, zorder=0)


# Optional: Add background shading up to 100% behind the bars
ax = plt.gca()
for bar in bars:
    ax.add_patch(
        plt.Rectangle(
            (bar.get_x(), 0),
            bar.get_width(),
            100,
            color="grey",
            alpha=0.1,
            zorder=0
        )
    )

# Add shared condition labels below group clusters
plt.text(0.5, -10, "<40 (0.05, 0)", ha="center", fontsize=12, transform=plt.gca().transData)
plt.text(4, -10, "300 (0.05, 0)", ha="center", fontsize=12, transform=plt.gca().transData)

plt.tight_layout()
plt.show()
