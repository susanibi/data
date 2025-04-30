import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import gaussian_kde
from io import StringIO
from matplotlib.colors import to_rgb, to_hex


# Function to darken a given color (hex string) by a specified factor.
def darken_color(color, factor=0.7):
    rgb = to_rgb(color)
    darker_rgb = tuple(c * factor for c in rgb)
    return to_hex(darker_rgb)


# Define your custom color palette mapping for each Sample ID category.
custom_palette = {
    "Control": "#87ceeb",  # Soft, sky blue
    "cap": "#b0e0e6",      # r
    "pt": "#ccccff",       # Calming teal
    "+FA, pt": "#b0c4de",  # Soft pastel yellow
    "+MQ, pt": "#e6e6fa"   # Deep navy blue
}

# Define the data with ProtGroups
data = """
Sample ID\tProtGroups
Control\t4599
Control\t4232
Control\t4738
Control\t4958
Control\t4671
cap\t914
cap\t0
cap\t1173
cap\t1941
cap\t1986
cap\t2361
cap\t3026
cap\t1795
pt\t258
pt\t6
pt\t0
pt\t0
pt\t2046
pt\t0
pt\t0
pt\t0
+FA, pt\t315
+FA, pt\t1710
+FA, pt\t2484
+FA, pt\t2679
+FA, pt\t2747
+FA, pt\t1750
+FA, pt\t2715
+FA, pt\t2704
+MQ, pt\t1749
+MQ, pt\t1039
+MQ, pt\t1509
+MQ, pt\t1704
"""

# Load data into a DataFrame.
df = pd.read_csv(StringIO(data), sep="\t")

# Create the figure and axis.
plt.figure(figsize=(10,6))
ax = plt.gca()

# Draw the violin plot without internal summary lines.
sns.violinplot(
    data=df,
    x="Sample ID",
    y="ProtGroups",
    hue="Sample ID",
    palette=custom_palette,
    legend=False,
    inner=None,
    #cut=0.3  # slight extension beyond the actual data
)



# For each category, compute summary stats and overlay custom summary lines.
# Note: Seaborn positions categories at x = 0, 1, 2, ... in the order they appear.
categories = list(df["Sample ID"].unique())

# Iterate through each category
for i, cat in enumerate(categories):
    group_data = df[df["Sample ID"] == cat]["ProtGroups"]

    # Calculate summary statistics.
    median_val = group_data.median()
    q1 = group_data.quantile(0.25)
    q3 = group_data.quantile(0.75)
    min_val = group_data.min()
    max_val = group_data.max()

    # Compute the kernel density estimate (KDE) for this group's data.
    kde = gaussian_kde(group_data)
    # Evaluate KDE across a grid spanning the group's range.
    y_grid = np.linspace(group_data.min(), group_data.max(), 200)
    density_values = kde(y_grid)
    dens_max = density_values.max()


    # Function to compute horizontal half-width for a given statistic.
    # Using 0.4 as the max half-width (violin width scaling from seaborn's default of width=0.8).
    def get_violin_half_width(stat_value):
        density_at_stat = kde(stat_value)
        return (density_at_stat / dens_max) * 0.4


    # Get the half-widths for each statistic.
    median_half_width = get_violin_half_width(median_val)
    q1_half_width = get_violin_half_width(q1)
    q3_half_width = get_violin_half_width(q3)
    min_half_width = get_violin_half_width(min_val)
    max_half_width = get_violin_half_width(max_val)

    # Derive a darker color based on the violin's color.
    line_color = darken_color(custom_palette[cat], factor=0.7)

    # Draw the median line as a solid line, less weighted (thinner).
    ax.hlines(
        median_val,
        i - median_half_width,
        i + median_half_width,
        color=line_color,
        linestyles='solid',
        linewidth=1  # Thinner line
    )

    # Draw the first and third quartile lines as dotted lines.
    ax.hlines(
        q1,
        i - q1_half_width,
        i + q1_half_width,
        color=line_color,
        linestyles='dotted',
        linewidth=0.8
    )
    ax.hlines(
        q3,
        i - q3_half_width,
        i + q3_half_width,
        color=line_color,
        linestyles='dotted',
        linewidth=0.8
    )

    # Draw the min and max as solid lines with same styling as median
    ax.hlines(
        min_val,
        i - min_half_width,
        i + min_half_width,
        color=line_color,
        linestyles='solid',
        linewidth=0.8
    )
    ax.hlines(
        max_val,
        i - max_half_width,
        i + max_half_width,
        color=line_color,
        linestyles='solid',
        linewidth=0.8
    )

# Set the font size for x and y axis labels and ticks
plt.xlabel("", fontsize=16)
plt.ylabel("ProtGroups", fontsize=16)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16 )


plt.title("")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()
