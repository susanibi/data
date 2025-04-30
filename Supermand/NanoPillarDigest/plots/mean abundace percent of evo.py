# Peptide Abundance Visualization Script
# This script uses the datasets:
# - P1_report.pr_matrix.tsv_processed.csv
# - P2_Scaled by mean.csv
# It calculates peptide abundance relative to Evo (%) with dynamic filtration and error bars.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Patch

# Load datasets
p1 = pd.read_csv('P1_report.pr_matrix.tsv_processed.csv')
p2 = pd.read_csv('P2_Scaled by mean.csv')

# Define conditions
f_bases = ['F1_0', 'F2_0'] + [f'F_{i}' for i in range(1, 11)]
r_bases = ['R1_0', 'R2_0'] + [f'R_{i}' for i in range(1, 11)]
labels = ['Evo', 'Plate', '0 (1)', '0 (2)'] + [str(i) for i in range(1, 11)]

# Dynamic filtration, imputation, mean & SE calculation
def process_condition(df, condition_base):
    replicates = [col for col in df.columns if col.startswith(condition_base + ".")]
    condition_data = df[replicates].copy()

    num_reps = len(replicates)
    threshold = 2 if num_reps == 3 else 3

    detection_counts = (condition_data > 0).sum(axis=1)
    condition_data[detection_counts < threshold] = 0

    condition_data_imputed = condition_data.replace(0, 1)
    mean_abundance = condition_data_imputed.mean().mean()
    se_abundance = condition_data_imputed.stack().std(ddof=1) / np.sqrt(condition_data_imputed.stack().count())

    return mean_abundance, se_abundance

# Process Evo and Plate
evo_raw_mean, evo_raw_se = process_condition(p1, 'Evo_1')
plate_raw_mean, plate_raw_se = process_condition(p1, 'Plate_1')

# Process F and R conditions
f_raw_means, f_raw_ses = [], []
r_raw_means, r_raw_ses = [], []

for base in f_bases:
    df = p2 if base in ['F1_0', 'F2_0'] or int(base.split('_')[1]) <=5 else p1
    mean_abundance, se_abundance = process_condition(df, base)
    f_raw_means.append(mean_abundance)
    f_raw_ses.append(se_abundance)

for base in r_bases:
    df = p2 if base in ['R1_0', 'R2_0'] or int(base.split('_')[1]) <=5 else p1
    mean_abundance, se_abundance = process_condition(df, base)
    r_raw_means.append(mean_abundance)
    r_raw_ses.append(se_abundance)

# Normalize to Evo
f_raw_plot = [100, (plate_raw_mean / evo_raw_mean) * 100] + [(val / evo_raw_mean) * 100 for val in f_raw_means]
r_raw_plot = [0, 0] + [(val / evo_raw_mean) * 100 for val in r_raw_means]

f_raw_se_plot = [evo_raw_se / evo_raw_mean * 100, plate_raw_se / evo_raw_mean * 100] + [(se / evo_raw_mean) * 100 for se in f_raw_ses]
r_raw_se_plot = [0, 0] + [(se / evo_raw_mean) * 100 for se in r_raw_ses]

# Colors and Legend
total_bars = len(labels)
f_colors = ['rosybrown', 'sienna'] + list(cm.BuGn(np.linspace(0.3, 1.0, total_bars - 2)))
r_colors = ['white', 'white'] + list(cm.Blues(np.linspace(0.3, 1.0, total_bars - 2)))

legend_elements = [
    Patch(facecolor='rosybrown', label='Evo'),
    Patch(facecolor='sienna', label='Plate'),
    Patch(facecolor=cm.BuGn(0.7), label='F'),
    Patch(facecolor=cm.Blues(0.7), label='R')
]

# Plotting
fig, ax = plt.subplots(figsize=(16, 6))
x = np.arange(total_bars)
width = 0.4

ax.bar(x - width/2, f_raw_plot, width, color=f_colors, zorder=3, yerr=f_raw_se_plot, capsize=5)
ax.bar(x + width/2, r_raw_plot, width, color=r_colors, zorder=3, yerr=r_raw_se_plot, capsize=5)

ax.yaxis.grid(True, linestyle='--', linewidth=0.5, zorder=0)
ax.set_axisbelow(True)

ax.set_ylabel('%')
ax.set_title('Peptide Abundance Relative to Evo (%)')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(handles=legend_elements)

plt.tight_layout()
plt.show()
