# Install if needed
# !pip install pandas matplotlib numpy

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import re

# ==== USER CONFIG ====
use_log2 = False  # 🔥 true= log2(x+1), false =raw
# =====================

# Step 1: Pick the GravyScore file
root = tk.Tk()
root.withdraw()

print("📂 Please select the 'Digest_HeLa_David_Exp002 - merged.csv' file:")
file_gravy = filedialog.askopenfilename(title="Select GravyScore CSV")

# Step 2: Load the file
data_gravy = pd.read_csv(file_gravy)

# Step 3: Melt into long format
id_vars = ['GravySequence', 'GravyScore', 'Precursor.Charge']
value_vars = [col for col in data_gravy.columns if col not in id_vars]

long_data = data_gravy.melt(id_vars=id_vars, value_vars=value_vars,
                            var_name='Sample', value_name='Intensity')

# Step 4: Clean Sample Names (remove .1, .2, .3 replicates)
long_data['BaseSample'] = long_data['Sample'].str.replace(r'\.\d+$', '', regex=True)

# Step 5: Bin GravyScore into 20 bins
long_data['GravyScore_bin'] = pd.cut(long_data['GravyScore'], bins=20)

# Step 6: Group by BaseSample and GravyScore_bin, average RAW Intensity
grouped = long_data.groupby(['BaseSample', 'GravyScore_bin'], observed=True)['Intensity'].mean().reset_index()

# Step 7: Apply log2(x+1) AFTER averaging if selected
if use_log2:
    grouped['PlotValue'] = np.log2(grouped['Intensity'] + 1)
    plot_label = 'Mean Log2(Intensity)'
else:
    grouped['PlotValue'] = grouped['Intensity']
    plot_label = 'Mean Raw Intensity'

# Step 8: Pivot for heatmap
heatmap_data = grouped.pivot(index='BaseSample', columns='GravyScore_bin', values='PlotValue')

# Step 9: Sorting the samples
def sort_key(sample_name):
    if sample_name.startswith('QC'):
        return (0, sample_name)
    else:
        parts = sample_name.split('_')
        surface = parts[0]  # 3p2, 3p5, etc.
        amount = parts[1]   # 50pg or 250pg
        extraction = parts[2]  # ACN or NoACN

        surface_order = {'3p2': 0, '3p5': 1, '5p5': 2}
        extraction_order = {'ACN': 0, 'NoACN': 1}
        amount_order = {'50pg': 0, '250pg': 1}

        return (1 + amount_order.get(amount, 99),
                extraction_order.get(extraction, 99),
                surface_order.get(surface, 99),
                sample_name)

# Step 10: Sort the samples
sorted_samples = sorted(heatmap_data.index, key=sort_key)
heatmap_data = heatmap_data.loc[sorted_samples]

# Step 11: Plot the heatmap
fig, ax = plt.subplots(figsize=(16, 12))
cax = ax.imshow(heatmap_data.values, cmap='viridis', aspect='auto', interpolation='nearest')

ax.set_xticks(np.arange(len(heatmap_data.columns)))
ax.set_yticks(np.arange(len(heatmap_data.index)))

ax.set_xticklabels([f"{interval.left:.2f}" for interval in heatmap_data.columns], rotation=45, fontsize=12)
ax.set_yticklabels(heatmap_data.index)

fig.colorbar(cax, ax=ax)
ax.set_title(plot_label, fontsize=14)
ax.set_xlabel('GravyScore Bin (lower bound)', fontsize=14)
ax.set_ylabel('')

plt.tight_layout()
plt.show()
