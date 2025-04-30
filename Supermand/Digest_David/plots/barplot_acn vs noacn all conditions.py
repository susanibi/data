
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import tkinter as tk
from tkinter import filedialog

# Use Tkinter to select the CSV file
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="Select the merged peptide intensity CSV file")

# Load the data
df = pd.read_csv(file_path)
df = df.loc[:, (df != 0).any(axis=0)]
df = df[[col for col in df.columns if 'pg_ACN' in col or 'pg_NoACN' in col]]

# Parameters
fontsize = 14  # Base font size
title_fontsize = fontsize + 2  # Larger for titles
small_fontsize = fontsize - 4  # Smaller for stats text

chips = ["3p2", "3p5", "5p5"]
loads = ["50pg", "250pg"]
colors = {
    '3.2': '#A3B3C2',  # blue
    '3.5': '#5F9EA0',  # soft teal
    '5.5': '#C4B49D'  # sand
}

# Data collection
results = []
plot_data = []


def get_log2_means(df, chip, load, group):
    cols = [col for col in df.columns if col.startswith(f"{chip}_{load}_{group}")]
    return np.log2(df[cols].mean(axis=1) + 1)


for chip in chips:
    for load in loads:
        acn = get_log2_means(df, chip, load, "ACN")
        noacn = get_log2_means(df, chip, load, "NoACN")
        if acn.empty or noacn.empty:
            continue

        t_stat, p_val = ttest_ind(acn, noacn, equal_var=False)
        chip_label = chip.replace("p", ".")

        results.append({
            "Chip": chip_label,
            "Load": load,
            "t": round(t_stat, 2),
            "p": p_val
        })

        plot_data.append({
            "Chip": chip_label, "Load": load, "Group": "ACN",
            "Mean": acn.mean(), "SE": acn.sem()
        })
        plot_data.append({
            "Chip": chip_label, "Load": load, "Group": "NoACN",
            "Mean": noacn.mean(), "SE": noacn.sem()
        })

results_df = pd.DataFrame(results)
plot_df = pd.DataFrame(plot_data)


def plot_group(data, load_label, filename):
    # Create figure with adequate margins
    fig = plt.figure(figsize=(10, 8), dpi=300)

    # Create axes with specific position
    # [left, bottom, width, height]
    ax = fig.add_axes([0.15, 0.25, 0.75, 0.65])

    # Add title with precise positioning
    fig.text(0.5, 0.92, f"Extraction ({load_label})",
             ha='center', fontsize=title_fontsize, weight='bold')

    width = 0.30  # Narrower bars to fit all on x-axis
    chips = ["3.2", "3.5", "5.5"]
    x = np.arange(len(chips))

    # Create positions for all bars
    positions = {}
    tick_positions = []
    tick_labels = []

    for i, chip in enumerate(chips):
        # Position ACN bar to the left of center, NoACN to the right
        positions[(chip, "ACN")] = x[i] - width / 2
        positions[(chip, "NoACN")] = x[i] + width / 2

        # Add tick positions and custom labels
        tick_positions.append(x[i])
        tick_labels.append(f"Chip {chip}")

    # Plot the bars
    for i, chip in enumerate(chips):
        try:
            # Get ACN and NoACN data for this chip
            acn_row = data[(data["Chip"] == chip) & (data["Group"] == "ACN")].iloc[0]
            noacn_row = data[(data["Chip"] == chip) & (data["Group"] == "NoACN")].iloc[0]

            # Get t-test results
            t_result = results_df[(results_df["Chip"] == chip) & (results_df["Load"] == acn_row["Load"])].iloc[0]

            # Plot the bars
            ax.bar(positions[(chip, "ACN")], acn_row["Mean"], width,
                   yerr=acn_row["SE"], color=colors[chip],
                   label=f"ACN" if i == 0 else "")

            ax.bar(positions[(chip, "NoACN")], noacn_row["Mean"], width,
                   yerr=noacn_row["SE"], color=colors[chip], alpha=0.4,
                   label=f"NoACN" if i == 0 else "")

            # Add statistical annotation
            p_val = t_result["p"]
            stars = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else ''

            ax.text(x[i], max(acn_row["Mean"], noacn_row["Mean"]) + 0.7,
                    f"t={t_result['t']}\np={p_val:.2e}\n{stars}",
                    ha='center', va='bottom', fontsize=small_fontsize)
        except:
            continue

    # Set x-axis ticks and labels
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, fontsize=fontsize)

    # Set y-axis label
    ax.set_ylabel("Mean Log2(x+1) Intensity", fontsize=fontsize)

    # Set tick parameters
    ax.tick_params(axis='both', which='major', labelsize=fontsize)

    # Create a simple legend for ACN vs NoACN
    handles = [
        plt.Rectangle((0, 0), 1, 1, color='gray'),
        plt.Rectangle((0, 0), 1, 1, color='gray', alpha=0.4)
    ]
    labels = ['ACN', 'NoACN']

    # Position legend at the bottom center
    ax.legend(handles, labels, loc='upper center',
              bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False,
              fontsize=fontsize)

    # Set y-axis limits and grid
    ax.set_ylim(0, data["Mean"].max() + data["SE"].max() + 2.5)
    ax.set_axisbelow(True)
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)

    # Create informative x-axis label
    fig.text(0.5, 0.12, "Chip Type", ha='center', fontsize=fontsize)

    # Save figure
    plt.savefig(filename, bbox_inches='tight', dpi=300)
    plt.show()


# Create both figures
plot_group(plot_df[plot_df["Load"] == "50pg"], "50pg", "Extraction_50pg_Log2_Plot.png")
plot_group(plot_df[plot_df["Load"] == "250pg"], "250pg", "Extraction_250pg_Log2_Plot.png")
print("Plots saved: Extraction_50pg_Log2_Plot.png and Extraction_250pg_Log2_Plot.png")
# # Parameters
# chips = ["3p2", "3p5", "5p5"]
# loads = ["50pg", "250pg"]
# colors = {
#     '3.2': '#A3B3C2',   # blue
#     '3.5': '#5F9EA0',   # soft teal
#     '5.5': '#C4B49D'    # sand
# }
#
# # Data collection
# results = []
# plot_data = []
#
# def get_log2_means(df, chip, load, group):
#     cols = [col for col in df.columns if col.startswith(f"{chip}_{load}_{group}")]
#     return np.log2(df[cols].mean(axis=1) + 1)
#
# for chip in chips:
#     for load in loads:
#         acn = get_log2_means(df, chip, load, "ACN")
#         noacn = get_log2_means(df, chip, load, "NoACN")
#         if acn.empty or noacn.empty:
#             continue
#
#         t_stat, p_val = ttest_ind(acn, noacn, equal_var=False)
#         chip_label = chip.replace("p", ".")
#
#         results.append({
#             "Chip": chip_label,
#             "Load": load,
#             "t": round(t_stat, 2),
#             "p": p_val
#         })
#
#         plot_data.append({
#             "Chip": chip_label, "Load": load, "Group": "ACN",
#             "Mean": acn.mean(), "SE": acn.sem()
#         })
#         plot_data.append({
#             "Chip": chip_label, "Load": load, "Group": "NoACN",
#             "Mean": noacn.mean(), "SE": noacn.sem()
#         })
#
# results_df = pd.DataFrame(results)
# plot_df = pd.DataFrame(plot_data)
#
# def plot_group(data, load_label, filename, font_size=16):
#     fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
#     plt.rcParams.update({'font.size': font_size})
#     width = 0.35
#     chips = ["3.2", "3.5", "5.5"]
#     x = range(len(chips))
#
#     for i, chip in enumerate(chips):
#         acn = data[(data["Chip"] == chip) & (data["Group"] == "ACN")].iloc[0]
#         noacn = data[(data["Chip"] == chip) & (data["Group"] == "NoACN")].iloc[0]
#         t_result = results_df[(results_df["Chip"] == chip) & (results_df["Load"] == acn["Load"])].iloc[0]
#
#         ax.bar(i - width/2, acn["Mean"], width, yerr=acn["SE"], color=colors[chip], label=f"{chip} ACN")
#         ax.bar(i + width/2, noacn["Mean"], width, yerr=noacn["SE"], color=colors[chip], alpha=0.4, label=f"{chip} NoACN")
#
#         p_val = t_result["p"]
#         if p_val < 0.001:
#             stars = '***'
#         elif p_val < 0.01:
#             stars = '**'
#         elif p_val < 0.05:
#             stars = '*'
#         else:
#             stars = ''
#
#         ax.text(i, max(acn["Mean"], noacn["Mean"]) + 0.7,
#                 f"t={t_result['t']}\np={p_val:.2e}\n{stars}",
#                 ha='center', va='bottom', fontsize=font_size)
#
#     ax.set_xticks(x)
#     ax.set_xticklabels(chips, fontsize=font_size)
#     ax.set_ylabel("Mean Log2(x+1) Intensity", fontsize=font_size)
#     ax.set_title(f"Extraction ({load_label})", fontsize=font_size + 2)
#     ax.set_ylim(0, data["Mean"].max() + data["SE"].max() + 2.5)
#     ax.set_axisbelow(True)
#     ax.legend(title="Chip Extraction", bbox_to_anchor=(1.05, 1), loc='upper left', frameon=False, fontsize=font_size, title_fontsize=font_size)
#     plt.tight_layout()
#     ax.grid(True, axis='y', linestyle='--', alpha=0.5)
#
#
#     # Show and save
#     plt.savefig(filename, bbox_inches='tight')
#     plt.show()
#
# # Create both figures
# plot_group(plot_df[plot_df["Load"] == "50pg"], "50", "Extraction_50pg_Log2_Plot.png", font_size=12)
# plot_group(plot_df[plot_df["Load"] == "250pg"], "250", "Extraction_250pg_Log2_Plot.png", font_size=12)
# print("Plots saved: Extraction_50pg_Log2_Plot.png and Extraction_250pg_Log2_Plot.png")
