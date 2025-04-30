
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from tkinter import Tk, filedialog

def get_mean_se(df, condition_base):
    replicates = [col for col in df.columns if col.startswith(condition_base + ".")]
    counts = [(df[rep] > 0).sum() for rep in replicates]
    mean_count = np.mean(counts)
    se_count = np.std(counts, ddof=1) / np.sqrt(len(counts))
    return mean_count, se_count

# Suppress Tkinter root window
root = Tk()
root.withdraw()

# Ask user to select two files
print("Select P1 CSV file")
p1_file = filedialog.askopenfilename(title="Select P1 CSV file")
print("Select P2 CSV file")
p2_file = filedialog.askopenfilename(title="Select P2 CSV file")

# Load data
p1 = pd.read_csv(p1_file)
p2 = pd.read_csv(p2_file)

# Define condition bases
f_bases = ['F1_0', 'F2_0'] + [f'F_{i}' for i in range(1, 11)]
r_bases = ['R1_0', 'R2_0'] + [f'R_{i}' for i in range(1, 11)]
labels = ['0 (1)', '0 (2)'] + [str(i) for i in range(1, 11)]

# Calculate means and SEs
f_means, f_ses = [], []
r_means, r_ses = [], []

for base in f_bases:
    if base in ['F1_0', 'F2_0'] or int(base.split('_')[1]) <=5:
        mean_count, se_count = get_mean_se(p2, base)
    else:
        mean_count, se_count = get_mean_se(p1, base)
    f_means.append(mean_count)
    f_ses.append(se_count)

for base in r_bases:
    if base in ['R1_0', 'R2_0'] or int(base.split('_')[1]) <=5:
        mean_count, se_count = get_mean_se(p2, base)
    else:
        mean_count, se_count = get_mean_se(p1, base)
    r_means.append(mean_count)
    r_ses.append(se_count)

# Plotting
total_bars = len(labels)
f_colors = cm.BuGn(np.linspace(0.3, 1.0, total_bars))
r_colors = cm.Blues(np.linspace(0.3, 1.0, total_bars))

fig, ax = plt.subplots(figsize=(14, 6))
x = np.arange(total_bars)
width = 0.4

ax.bar(x - width/2, f_means, width, color=f_colors, label='F', zorder=3, yerr=f_ses, capsize=5)
ax.bar(x + width/2, r_means, width, color=r_colors, label='R', zorder=3, yerr=r_ses, capsize=5)

ax.yaxis.grid(True, linestyle='--', linewidth=0.5, zorder=0)
ax.set_axisbelow(True)

ax.set_ylabel('Peptide IDs')
ax.set_title('Detected Peptides')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

plt.tight_layout()
plt.show()
