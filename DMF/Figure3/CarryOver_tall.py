import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Data input
data = {
    "Round": [
        "Round1"] * 4 + ["Round2"] * 4 + ["Round3"] * 4 + ["Round4"] * 4 + ["Round5"] * 4,
    "Sample": list(range(1, 21)),
    "ProtID": [1141, 454, 741, 0, 1059, 0, 876, 654, 0, 369, 373, 0, None, 1, 0, 675, 2180, 330, 0, 7],
    "Wash (+2 µl FA)": [0, 2, 0, 118, 135, 0, 456, 708, 959, 1770, 1094, 1301, None, 655, 784, 950, 846, 0, 0, 0]
}

df = pd.DataFrame(data).dropna()

# Colors
prot_color = "#264653"
wash_color = "#a8dadc"

def format_sample_label(sample_id):
    return f"Sample {sample_id}"

rounds = df['Round'].unique()
fig, axes = plt.subplots(len(rounds), 1, figsize=(12, 5 * len(rounds)), sharex=False)

spacing = 2  # Increased spacing
bar_width = 0.4

for i, rnd in enumerate(rounds):
    sub = df[df['Round'] == rnd].reset_index(drop=True)
    x = [j * spacing for j in range(len(sub))]
    sample_ids = sub['Sample'].astype(int).tolist()

    ax = axes[i] if len(rounds) > 1 else axes

    # Plot bars
    ax.bar([p - bar_width/2 for p in x], sub['ProtID'], width=bar_width, color=prot_color)
    ax.bar([p + bar_width/2 for p in x], sub['Wash (+2 µl FA)'], width=bar_width, color=wash_color, alpha=0.85)

    ax.set_title(f'{rnd}', loc='left', fontsize=12, weight='bold')

    # Set xticks and custom labels
    ax.set_xticks(x)
    ax.set_xticklabels([format_sample_label(sid) for sid in sample_ids], rotation=45, ha='right', color='black')

    # Add 3 vertical dividers *between* wells
    for j in range(1, 4):  # after well 1 to well 3
        xpos = spacing * j - spacing / 2
        ax.axvline(x=xpos, color='lightgray', linestyle='--', linewidth=0.7)

    # Well labels inside each bar group
    ymax = max(sub[['ProtID', 'Wash (+2 µl FA)']].max()) * 1.1
    for j, xpos in enumerate(x):
        well_label = f"Well {j + 1}"
        ax.text(xpos, ymax, well_label, ha='center', va='bottom', fontsize=10, color='black')

    ax.set_ylabel('Intensity')

# One clean bottom legend
handles = [
    plt.Line2D([0], [0], color=prot_color, lw=8, label='ProtID'),
    plt.Line2D([0], [0], color=wash_color, lw=8, label='Wash (+2 µl FA)')
]
fig.legend(handles=handles, loc='lower center', ncol=2, fontsize=12)

# Layout spacing adjustments
plt.subplots_adjust(bottom=0.15, hspace=0.5)
plt.tight_layout(rect=[0, 0.1, 1, 1])  # More room at bottom
plt.show()

