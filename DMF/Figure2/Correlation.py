import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from io import StringIO

# ---- Hardcoded dataset ----
data = """Cell Type,Cell Conc,F68 (%),RG (%),Temp,Split efficiency (%)
HEK,≤40,0.02,0,25,97.27
HEK,≤40,0.02,0.05,25,96.88
HEK,≤40,0.05,0.15,25,100
HEK,≤40,0.05,0,25,100
HEK,≤40,0.05,0,25,98.44
HEK,100,0.01,0,25,5
HEK,200,0.01,0,25,0
HEK,200,0.01,0,25,9.38
HEK,200,0.02,0,25,1.56
HEK,200,0.02,0.01,25,65.23
HEK,200,0.03,0,25,9.38
HEK,200,0.04,0,25,50
HEK,300,0,0,25,0
HEK,300,0,0,25,0
HEK,300,0,0,25,0
HEK,300,0,0.05,25,10.94
HEK,300,0.01,0,25,5
HEK,300,0.01,0.05,25,100
HEK,300,0.05,0,25,90.63
HEK,300,0.05,0,25,78.13
HEK,300,0.05,0,25,93.36
HEK,300,0.05,0,56,98.44
HEK,400,0.01,0,25,53.13
HEK,400,0.02,0.01,25,64"""

# Load data and clean column names
df = pd.read_csv(StringIO(data))
df.columns = [col.strip() for col in df.columns]

# Create group labels (e.g., "100 (n=1)" or "≤40 (n=5)")
df["Conc Group Exact"] = df["Cell Conc"].astype(str)
group_counts = df["Conc Group Exact"].value_counts().to_dict()
df["Group Label"] = df["Conc Group Exact"].apply(
    lambda x: f"{x} (n={group_counts.get(x, 0)})"
)

# --- Custom Colors ---
# Create a palette from Seaborn's "Set2" for 5 groups.
# For group "100", override with a more blue color.
set2_palette = sns.color_palette("Set2", 5)
custom_colors = {
    "≤40": "#7093B6",  # Muted blue
    "100": "#66A3C2",  # Lighter blue
    "200": "#748D8E",  # Transitional tone (a soft periwinkle, bridging blue to purple)
    "300": "#C89BB7",
    "400": "#915F6D"   # Muted mauve
}
# Global plotting parameters
plt.figure(figsize=(10, 6))
font_size = 14
title_font_size = font_size + 1
tick_font_size = font_size - 1

# For scatter, s is the marker area (points^2)
scatter_marker_area = 90  # Uniform marker area for scatter markers
rg_linewidth_scale = 30  # Scaling factor for RG% to edge width

# --- Define Custom Plotting Order ---
# Your desired plotting order was defined earlier.
# For example, suppose you want the markers drawn in this order:
# 200 - 300 - ≤40 - 400 - 100.
# (We already set that ordering in your previous custom_order_list.)
custom_order = ["200", "300", "≤40", "400", "100"]
custom_order_list = []
for token in custom_order:
    for label in df["Group Label"].unique():
        if label.startswith(token):
            custom_order_list.append(label)

# For plotting, we still use the custom_order_list.
# We also create a zorder mapping so that each token is drawn appropriately.
zorder_map = {}
for i, token in enumerate(custom_order):
    # Later tokens get a higher zorder (drawn on top)
    zorder_map[token] = i + 1

# Plot each group in the custom plotting order
for label in custom_order_list:
    group_data = df[df["Group Label"] == label]
    group_token = label.split()[0]
    color = custom_colors.get(group_token, set2_palette[0])
    z = zorder_map.get(group_token, 1)

    plt.scatter(
        x=group_data["F68 (%)"],
        y=group_data["Split efficiency (%)"],
        s=scatter_marker_area,
        alpha=0.9,
        color=color,
        edgecolors="black",  # Black edge encodes RG%
        linewidths=group_data["RG (%)"] * rg_linewidth_scale,
        marker='o',
        zorder=z
    )

    if group_data["F68 (%)"].nunique() > 1:
        sns.regplot(
            data=group_data,
            x="F68 (%)",
            y="Split efficiency (%)",
            scatter=False,
            color=color,
            line_kws={"linewidth": 2}
        )
        line = plt.gca().lines[-1]
        line.set_zorder(z - 0.1)

# --- Build Legend in a Different Order ---
# Desired legend order: ≤40, 100, 200, 300, then 400.
desired_legend_order = ["≤40", "100", "200", "300", "400"]
legend_handles_ordered = []
# Iterate over the desired tokens and pick the corresponding group label
for token in desired_legend_order:
    # Find the group label that starts with the token
    for label in df["Group Label"].unique():
        if label.startswith(token):
            # Create a legend handle for this label
            color = custom_colors.get(token, set2_palette[0])
            handle = mlines.Line2D(
                [], [],
                marker='o',
                markersize=14,  # larger markers for the group legend
                markerfacecolor=color,
                markeredgecolor="white",  # uniform white edge
                markeredgewidth=2,
                linestyle='None',
                label=label
            )
            legend_handles_ordered.append(handle)
            break  # once found, move to the next token

# --- Create Custom Legend Handles for RG Contribution ---
rg_marker_size = 8  # Smaller markers for the RG legend
rg_handle_low = mlines.Line2D(
    [], [],
    marker='o',
    markersize=rg_marker_size,
    markerfacecolor="white",  # white fill
    markeredgecolor="black",
    markeredgewidth=1,  # thin edge for Low RG%
    linestyle='None',
    label='Low RG%'
)
rg_handle_high = mlines.Line2D(
    [], [],
    marker='o',
    markersize=rg_marker_size,
    markerfacecolor="white",  # white fill
    markeredgecolor="black",
    markeredgewidth=3,  # thicker edge for High RG%
    linestyle='None',
    label='High RG%'
)

# --- Add Legends to the Plot ---
legend1 = plt.legend(
    handles=legend_handles_ordered,
    title="Cell Conc Group",
    fontsize=font_size,
    title_fontsize=font_size,
    bbox_to_anchor=(1.05, 1),
    loc='upper left'
)
plt.gca().add_artist(legend1)

legend2 = plt.legend(
    handles=[rg_handle_low, rg_handle_high],
    title="RG Contribution",
    fontsize=font_size,
    title_fontsize=font_size,
    bbox_to_anchor=(1.05, 0.5),
    loc='upper left'
)

# Final plot formatting
plt.title("", fontsize=title_font_size)
plt.xlabel("F68 (%)", fontsize=font_size)
plt.ylabel("Split Efficiency (%)", fontsize=font_size)
plt.xticks(fontsize=tick_font_size)
plt.yticks(fontsize=tick_font_size)
plt.grid(True)
plt.tight_layout()
plt.savefig("f68_vs_split_efficiency.png", dpi=300)
plt.show()
