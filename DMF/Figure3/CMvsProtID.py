import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# -------------------------
# Data Preparation
# -------------------------
sample_no = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
             11, 12, 13, 14, 15, 16, 17, 18]

cm = [1.2, 1.4, 1.4, 2.9, 1.1, 1.0, 2.9, 0.2, 1.5, 0.1,
      0.8, 0.2, 0.2, 0.8, 1.0, 0.2, 0.2, 0.4]

protein_ids = [3359, 994, 1847, 2699, 202, 2118, 1287, 160, 768, 777,
               1879, 0,   0,    2180, 330, 0,   7,    0]

# Create a DataFrame
df = pd.DataFrame({
    'Sample_No': sample_no,
    'cm': cm,
    'ProteinIDs': protein_ids
})

# Melt the DataFrame into a long format for flexibility
df_melted = df.melt(id_vars='Sample_No', var_name='Metric', value_name='Value')

# Define colors for the two metrics (adjust these if desired)
colors = {
    "cm": "#a9a9a9",
    "ProteinIDs": "#264653"
}

# -------------------------
# Font and Style Customization
# -------------------------
font_size = 18       # Change overall font size with this variable
font_color = 'black' # Change overall font color here

# -------------------------
# Determine positions for grouped bars
# -------------------------
# We want two bars per sample, so we set x positions using numpy:
x = np.arange(len(df))
bar_width = 0.35

# -------------------------
# Filter Melted Data for Each Metric
# -------------------------
df_cm = df_melted[df_melted['Metric'] == 'cm']
df_prot = df_melted[df_melted['Metric'] == 'ProteinIDs']

# -------------------------
# Plotting Setup: Dual y-axes
# -------------------------
fig, ax1 = plt.subplots(figsize=(12, 6))
ax2 = ax1.twinx()  # secondary y-axis for 'cm'

# Plot ProteinIDs on the primary y-axis (ax1)
bars_prot = ax1.bar(x - bar_width/2, df_prot['Value'].values, bar_width,
                    color=colors['ProteinIDs'], label='ProteinIDs')

# Plot cm on the secondary y-axis (ax2)
bars_cm = ax2.bar(x + bar_width/2, df_cm['Value'].values, bar_width,
                  color=colors['cm'], label='Capillary Fill Length (cm)')

# -------------------------
# Customize Axes, Ticks, and Labels
# -------------------------
# Set sample numbers as x tick labels
ax1.set_xticks(x)
ax1.set_xticklabels(df['Sample_No'], fontsize=font_size, color=font_color)
ax1.set_xlabel('Sample# (Single HEK, 0.05%F68)', fontsize=font_size, color=font_color)

# Set y-axis labels with distinct colors matching the bars
ax1.set_ylabel('ProteinIDs', fontsize=font_size, color=colors['ProteinIDs'])
ax2.set_ylabel('Capillary Fill Length (cm)', fontsize=font_size, color=colors['cm'])

# Adjust tick parameters for clarity
ax1.tick_params(axis='y', labelcolor=colors['ProteinIDs'], labelsize=font_size)
ax2.tick_params(axis='y', labelcolor=colors['cm'], labelsize=font_size)
ax1.tick_params(axis='x', labelsize=font_size, colors=font_color)

# Set the title of the plot
plt.title('', fontsize=font_size+2, color=font_color)

# -------------------------
# Create a Combined Legend
# -------------------------
legend_elements = [Patch(facecolor=colors['ProteinIDs'], label='ProteinIDs'),
                   Patch(facecolor=colors['cm'], label='CFL (cm)')]
ax1.legend(handles=legend_elements, loc='upper right', fontsize=font_size)

# Optimize the layout and display the plot
plt.tight_layout()
plt.show()
