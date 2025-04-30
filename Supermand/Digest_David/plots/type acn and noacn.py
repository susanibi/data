
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

# Prompt for file selection
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="Select your merged CSV file")

# Load the data
df = pd.read_csv(file_path)
df = df.loc[:, (df != 0).any(axis=0)]  # remove all-zero columns

# Define log2(x+1) peptide mean function
def get_log2_peptide_means(df, chip, load, group):
    cols = [col for col in df.columns if col.startswith(f"{chip}_{load}_{group}")]
    return np.log2(df[cols].mean(axis=1) + 1)

# Shared parameters
chips = ["3p5", "5p5"]
loads = ["50pg", "250pg"]
plot_configs = [("ACN", "SurfaceType_3.5_vs_5.5_ACN.png"), ("NoACN", "SurfaceType_3.5_vs_5.5_NoACN.png")]
colors = {
    ("3.5", "50pg"): '#4cb7af',
    ("3.5", "250pg"): '#008080',
    ("5.5", "50pg"): '#e4d2b0',
    ("5.5", "250pg"): '#c8af88'
}

for group, output_file in plot_configs:
    results = []
    plot_data = []

    for load in loads:
        g35 = get_log2_peptide_means(df, "3p5", load, group)
        g55 = get_log2_peptide_means(df, "5p5", load, group)
        t_stat, p_val = ttest_ind(g35, g55, equal_var=False)
        results.append({"Load": load, "t": round(t_stat, 2), "p": p_val})
        plot_data.append({"Chip": "3.5", "Load": load, "Mean": g35.mean(), "SE": g35.sem()})
        plot_data.append({"Chip": "5.5", "Load": load, "Mean": g55.mean(), "SE": g55.sem()})

    df_plot = pd.DataFrame(plot_data)
    df_stats = pd.DataFrame(results)

    # Plot
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    x = np.arange(len(loads))
    width = 0.35
    tick_positions = []
    tick_labels = []
    legend_entries = {}

    for i, chip in enumerate(["3.5", "5.5"]):
        for j, load in enumerate(loads):
            row = df_plot[(df_plot["Chip"] == chip) & (df_plot["Load"] == load)].iloc[0]
            xpos = x[j] + (i - 0.5) * width
            tick_positions.append(xpos)
            tick_labels.append(f"{chip}\n{load}")
            bar = ax.bar(xpos, row["Mean"], width, yerr=row["SE"], color=colors[(chip, load)])
            if chip not in legend_entries:
                legend_entries[chip] = bar

    for j, load in enumerate(loads):
        row = df_stats[df_stats["Load"] == load].iloc[0]
        stars = '***' if row["p"] < 0.001 else '**' if row["p"] < 0.01 else '*' if row["p"] < 0.05 else ''
        max_y = max(df_plot[df_plot["Load"] == load]["Mean"] + df_plot[df_plot["Load"] == load]["SE"])
        ax.text(x[j], max_y + 1.0, f"t={row['t']}\np={row['p']:.2e}\n{stars}", ha='center', fontsize=10)

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=14)
    ax.set_ylabel("Mean Log2(x+1) Intensity", fontsize=14)
    ax.set_title(f"Surface Type ({group})", fontsize=16)
    ax.set_ylim(0, df_plot["Mean"].max() + df_plot["SE"].max() + 3.0)
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    ax.legend(legend_entries.values(), legend_entries.keys(), title="Chip", frameon=False)
    plt.tight_layout()
    plt.savefig(output_file, bbox_inches='tight')
    plt.show()
