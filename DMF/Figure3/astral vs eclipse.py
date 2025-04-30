import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

# -------------------------
# Data Preparation
# -------------------------
data = {
    "ASTRAL": [3488, 3029, 3499, 3264, 3036, 2802, 3186, 3747, 3780, 3133, 3457, 3883, 4004],
    "Eclipse": [1657, 1923, 1625, 304, 959, 656, 1467, 1301, 2238, 2603, 1870, 784, np.nan]
}
df = pd.DataFrame(data)

# Calculate p-value using an independent t-test (dropping missing values)
astral_data = df['ASTRAL'].dropna()
eclipse_data = df['Eclipse'].dropna()
t_stat, p_value = ttest_ind(astral_data, eclipse_data)
print("p-value:", p_value)

# -------------------------
# Plot Settings and Customization Variables
# -------------------------
# Customize the color for the mean value text
mean_text_color = '#A9A9A9'

# Defining the positions for the two boxes (closer together)
data_list = [astral_data.values, eclipse_data.values]
positions = [1, 1.5]

plt.figure(figsize=(10, 8))
ax = plt.gca()

# Set horizontal gridlines in very light grey
ax.yaxis.grid(True, color='lightgrey', linestyle='--', linewidth=0.5)

# -------------------------
# Create the Boxplot
# -------------------------
box = ax.boxplot(data_list, positions=positions, patch_artist=True, widths=0.3, showmeans=False)

# Define colors for the boxes (e.g., teal for ASTRAL, dark blue for Eclipse)
box_colors = ['#93B9CC', '#5b9bbf'] #AStral, Eclipse
for patch, color in zip(box['boxes'], box_colors):
    patch.set_facecolor(color)

# Draw median lines in black with reduced weight
for median in box['medians']:
    median.set_color('black')
    median.set_linewidth(1)

ax.tick_params(axis='y', labelsize=16, colors='black')


# -------------------------
# Annotate Mean and Median Values
# -------------------------
for i, arr in enumerate(data_list):
    x_pos = positions[i]
    col_mean = np.mean(arr)
    col_mean_int = int(round(col_mean))
    col_median = np.median(arr)
    col_median_int = int(round(col_median))

    # Plot an "x" marker for the mean (using the customizable mean_text_color)
    ax.plot(x_pos, col_mean, marker='x', color=mean_text_color, markersize=8, mew=1)

    # Annotate the mean value directly under the "x" marker (centered at x_pos)
    #mean_offset = 60  # vertical offset (downward) from the mean position
    #ax.text(x_pos, col_mean - mean_offset, f"{col_mean_int}",
            #ha='center', va='top', fontsize=12, color=mean_text_color)

    # Retrieve the upper whisker value for this box.
    # The whiskers are in pairs: index 2*i (lower) and index 2*i+1 (upper).
    upper_whisker_line = box['whiskers'][2 * i + 1]
    ydata = upper_whisker_line.get_ydata()
    upper_whisker_value = ydata[1]

    # Annotate the median value just above the median line with a small offset
    median_offset = 10  # adjust this value as needed
    ax.text(x_pos, col_median_int + median_offset, f"{col_median_int}",
            ha='center', va='bottom', fontsize=16, color='black')

# -------------------------
# Final Plot Adjustments
# -------------------------
# Set the x-ticks and tick labels (the number of labels now matches the number of positions)
ax.set_xticks(positions)
ax.set_xticklabels(["ASTRAL", "Eclipse"], fontsize=16)

plt.ylabel("ProteinIDs", fontsize=16)
plt.title("", fontsize=14)
ax.set_ylim(0, 4500)

plt.tight_layout()
plt.show()
