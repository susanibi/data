
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import tkinter as tk
from tkinter import filedialog

# Open file selection dialog
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="Select merged peptide intensity CSV")

# Load data
df = pd.read_csv(file_path)
df = df.loc[:, (df != 0).any(axis=0)]
df = df[[col for col in df.columns if 'pg_ACN' in col or 'pg_NoACN' in col]]

# Helper to get peptide means
def get_log2_peptide_means(df, chip, load, group):
    cols = [col for col in df.columns if col.startswith(f"{chip}_{load}_{group}")]
    return np.log2(df[cols].mean(axis=1) + 1)


# Color palette (final soft teal + navy theme)
fontsize = 14  # Base font size
title_fontsize = fontsize + 2  # Slightly larger for titles
small_fontsize = fontsize - 4  # Smaller font for stats text

colors = {
    ("3.2", "50pg"): '#8db4c7',
    ("3.2", "250pg"): '#43698d',
    ("3.5", "50pg"): '#9dd9d2',
    ("3.5", "250pg"): '#3b9e9b'
}

# Build data
chips = ["3p2", "3p5"]
loads = ["50pg", "250pg"]
plot_data = []
ttest_data = []

for load in loads:
    m32 = get_log2_peptide_means(df, "3p2", load, "NoACN")
    m35 = get_log2_peptide_means(df, "3p5", load, "NoACN")
    t_stat, p_val = ttest_ind(m32, m35, equal_var=False)
    ttest_data.append({"Load": load, "t-statistic": round(t_stat, 2), "p-value": p_val})
    plot_data.append({"Chip": "3.2", "Load": load, "Mean": m32.mean(), "SE": m32.sem()})
    plot_data.append({"Chip": "3.5", "Load": load, "Mean": m35.mean(), "SE": m35.sem()})

df_plot = pd.DataFrame(plot_data)
df_stats = pd.DataFrame(ttest_data)

# Create figure with adequate margins
fig = plt.figure(figsize=(10, 8), dpi=300)  # Increased figure size

# Create axes with specific position
# [left, bottom, width, height]
ax = fig.add_axes([0.15, 0.25, 0.75, 0.65])  # Adjusted for more space

# Add title with precise positioning
fig.text(0.5, 0.95, "Position",
         ha='center', fontsize=title_fontsize, weight='bold')

x = np.arange(len(loads))
width = 0.35
tick_positions = []
tick_labels = []
legend_entries = {}

for i, chip in enumerate(["3.2", "3.5"]):
    for j, load in enumerate(loads):
        row = df_plot[(df_plot["Chip"] == chip) & (df_plot["Load"] == load)].iloc[0]
        xpos = x[j] + (i - 0.5) * width
        tick_positions.append(xpos)
        tick_labels.append(f"{chip}\n{load}")
        bar = ax.bar(xpos, row["Mean"], width, yerr=row["SE"], color=colors[(chip, load)])
        if chip not in legend_entries:
            legend_entries[chip] = bar

# Add t-stat annotations
for j, load in enumerate(loads):
    row = df_stats[df_stats["Load"] == load].iloc[0]
    stars = '***' if row["p-value"] < 0.001 else '**' if row["p-value"] < 0.01 else '*' if row["p-value"] < 0.05 else ''
    max_y = max(df_plot[df_plot["Load"] == load]["Mean"] + df_plot[df_plot["Load"] == load]["SE"])
    ax.text(x[j], max_y + 1.0, f"t={row['t-statistic']}\np={row['p-value']:.2e}\n{stars}",
            ha='center', va='bottom', fontsize=small_fontsize)

# Set font sizes for all text elements
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels, fontsize=fontsize)
ax.set_ylabel("Mean Log2(x+1) Intensity", fontsize=fontsize)

# Adding an explicit x-axis label
fig.text(0.5, 0.05, "Chip and Load", ha='center', fontsize=fontsize)

# Set tick parameters
ax.tick_params(axis='both', which='major', labelsize=fontsize)

ax.set_ylim(0, df_plot["Mean"].max() + df_plot["SE"].max() + 3.0)
ax.grid(True, axis='y', linestyle='--', alpha=0.5)
ax.set_axisbelow(True)

# Set legend with controlled font size
# legend = ax.legend(legend_entries.values(), legend_entries.keys(),
#                    title="Chip", frameon=False,
#                    loc='upper center', bbox_to_anchor=(0.5, -0.25))
#
# legend.get_title().set_fontsize(fontsize)
# for text in legend.get_texts():
#     text.set_fontsize(fontsize)

plt.savefig("Position_Comparison_3.2_vs_3.5_NoACN.png", bbox_inches='tight')
plt.show()
# # Color palette (final soft teal + navy theme)
# colors = {
#     ("3.2", "50pg"): '#8db4c7',
#     ("3.2", "250pg"): '#43698d',
#     ("3.5", "50pg"): '#9dd9d2',
#     ("3.5", "250pg"): '#3b9e9b'
# }
#
# # Build data
# chips = ["3p2", "3p5"]
# loads = ["50pg", "250pg"]
# plot_data = []
# ttest_data = []
#
# for load in loads:
#     m32 = get_log2_peptide_means(df, "3p2", load, "NoACN")
#     m35 = get_log2_peptide_means(df, "3p5", load, "NoACN")
#     t_stat, p_val = ttest_ind(m32, m35, equal_var=False)
#     ttest_data.append({"Load": load, "t-statistic": round(t_stat, 2), "p-value": p_val})
#     plot_data.append({"Chip": "3.2", "Load": load, "Mean": m32.mean(), "SE": m32.sem()})
#     plot_data.append({"Chip": "3.5", "Load": load, "Mean": m35.mean(), "SE": m35.sem()})
#
# df_plot = pd.DataFrame(plot_data)
# df_stats = pd.DataFrame(ttest_data)
#
# # Plotting
# fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
# x = np.arange(len(loads))
# width = 0.35
# tick_positions = []
# tick_labels = []
# legend_entries = {}
#
# for i, chip in enumerate(["3.2", "3.5"]):
#     for j, load in enumerate(loads):
#         row = df_plot[(df_plot["Chip"] == chip) & (df_plot["Load"] == load)].iloc[0]
#         xpos = x[j] + (i - 0.5) * width
#         tick_positions.append(xpos)
#         tick_labels.append(f"{chip}\n{load}")
#         bar = ax.bar(xpos, row["Mean"], width, yerr=row["SE"], color=colors[(chip, load)])
#         if chip not in legend_entries:
#             legend_entries[chip] = bar
#
# # Add t-stat annotations
# for j, load in enumerate(loads):
#     row = df_stats[df_stats["Load"] == load].iloc[0]
#     stars = '***' if row["p-value"] < 0.001 else '**' if row["p-value"] < 0.01 else '*' if row["p-value"] < 0.05 else ''
#     max_y = max(df_plot[df_plot["Load"] == load]["Mean"] + df_plot[df_plot["Load"] == load]["SE"])
#     ax.text(x[j], max_y + 1.0, f"t={row['t-statistic']}\np={row['p-value']:.2e}\n{stars}",
#             ha='center', va='bottom', fontsize=10)
#
# ax.set_xticks(tick_positions)
# ax.set_xticklabels(tick_labels, fontsize=11)
# ax.set_ylabel("Mean Log2(x+1) Intensity", fontsize=11)
# ax.set_title("Position", fontsize=13)
# ax.set_ylim(0, df_plot["Mean"].max() + df_plot["SE"].max() + 3.0)
# ax.grid(True, axis='y', linestyle='--', alpha=0.5)
# ax.set_axisbelow(True)
# ax.legend(legend_entries.values(), legend_entries.keys(), title="Chip", frameon=False)
# plt.tight_layout()
# plt.savefig("Position_Comparison_3.2_vs_3.5_NoACN.png", bbox_inches='tight')
# plt.show()
