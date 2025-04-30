import pandas as pd
import matplotlib.pyplot as plt

# Data
data = {
    "Round": [
        "Round1"] * 4 + ["Round2"] * 4 + ["Round3"] * 4 + ["Round4"] * 4 + ["Round5"] * 4,
    "Sample": list(range(1, 21)),
    "ProtID": [1141, 454, 741, 0, 1059, 0, 876, 654, 0, 369, 373, 0, None, 1, 0, 675, 2180, 330, 0, 7],
    "Wash (+2 µl FA)": [0, 2, 0, 118, 135, 0, 456, 708, 959, 1770, 1094, 1301, None, 655, 784, 950, 846, 0, 0, 0],
    "CFL": [1.2, 1.4, 1.1, None,
            2.9, 1.1, 1.0, 2.9,
            0.2, 1.5, 0.3, None,
            None, 0.2, 0.2, 0,
            0.8, 1.0, 0.2, 0.2]
}

# DataFrame
df = pd.DataFrame(data)

# Fill missing values with 0 (to preserve data integrity)
df["ProtID"] = df["ProtID"].fillna(0)
df["Wash (+2 µl FA)"] = df["Wash (+2 µl FA)"].fillna(0)
df["CFL"] = df["CFL"].fillna(0)

# Parameters
prot_color = "#264653"
wash_color = "#b0c4de"
cfl_color = "#a9a9a9"
bar_width = 0.32
spacing = 1.2
round_gap = 1.3  # space between rounds
wells_per_round = 4

# Generate x positions with equal spacing and fixed gap after each round (except the last)
x = []
labels = []
round_centers = []
current_x = 0
rounds = df["Round"].unique()

for rnd in rounds:
    indices = df[df["Round"] == rnd].index
    for i, idx in enumerate(indices):
        x.append(current_x)
        labels.append(f"Well {i+1}")
        current_x += spacing
    round_centers.append((rnd, sum(x[-wells_per_round:]) / wells_per_round))
    current_x += round_gap  # only adds gap *after* each round

# Trim the last gap
x = x[:len(df)]
x_cfl = [xi - bar_width for xi in x]
x_prot = [xi for xi in x]
x_wash = [xi + bar_width for xi in x]

# Plot
fig, ax1 = plt.subplots(figsize=(len(df) * 0.9, 5))

# Bars
bars_prot = ax1.bar(x_prot, df["ProtID"], width=bar_width, color=prot_color, label="Sample")
bars_wash = ax1.bar(x_wash, df["Wash (+2 µl FA)"], width=bar_width, color=wash_color, alpha=0.9, label="Residual")

# Secondary y-axis for CFL values
ax2 = ax1.twinx()
bars_cfl = ax2.bar(x_cfl, df["CFL"], width=bar_width, color=cfl_color, alpha=0.5, label="CFL")
ax2.set_ylabel("(Cm)", color=cfl_color, fontsize=16)
ax2.tick_params(axis='y', labelsize=16, labelcolor=cfl_color)

# Add text inside bars at the top
for i, bar in enumerate(bars_prot):
    if bar.get_height() > 0:
        round_number = i // wells_per_round + 1
        sample_number = i % wells_per_round + 1 + (round_number - 1) * wells_per_round
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 0.95, f"{sample_number}", ha='center', va='top', color='white', fontsize=10, rotation=0)

for i, bar in enumerate(bars_wash):
    if bar.get_height() > 0:
        round_number = i // wells_per_round + 1
        residual_number = i % wells_per_round + 1 + (round_number - 1) * wells_per_round
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 0.95, f"{residual_number}", ha='center', va='top', color='black', fontsize=8)

# X-axis ticks
ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=45, ha='center', fontsize=16)

# X-axis font size
ax1.set_xticklabels(labels, rotation=45, ha='center', fontsize=16)

# Y-axis font size
ax1.tick_params(axis='y', labelsize=16)
ax1.set_ylabel("ProteinIDs ", fontsize=16)

# Round separators (after rounds 1–4 only)
for i in range(1, len(rounds)):
    xpos = i * wells_per_round * spacing + (i - 0.7) * round_gap
    ax1.axvline(x=xpos, color='gray', linestyle='--', linewidth=0.8)

# Round labels centered over each group
ymax = max(df["ProtID"].max(), df["Wash (+2 µl FA)"].max())
for rnd, center in round_centers:
    ax1.text(center, ymax * 1.05, rnd, ha='center', va='bottom', fontsize=16, fontweight='bold')

# Set y-axis grid lines to lighter grey and behind the bars
ax1.grid(True, which='major', axis='y', color='#d3d3d3', linestyle='--', linewidth=0.7)
ax1.set_axisbelow(True)

# Combine legends
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc='upper right', fontsize=16)

plt.subplots_adjust(bottom=0.25, top=0.88, left=0.1, right=0.9)
plt.show()
