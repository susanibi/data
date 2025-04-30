
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Patch
from tkinter import Tk, filedialog

def get_mean_se(df, condition_base):
    replicates = [col for col in df.columns if col.startswith(condition_base + ".")]
    counts = [(df[rep] > 0).sum() for rep in replicates]
    mean_count = np.mean(counts)
    se_count = np.std(counts, ddof=1) / np.sqrt(len(counts))
    return mean_count, se_count

# Tkinter file dialog
root = Tk()
root.withdraw()

print("Select P1 CSV file")
p1_file = filedialog.askopenfilename(title="Select P1 CSV file")
print("Select P2 CSV file")
p2_file = filedialog.askopenfilename(title="Select P2 CSV file")

p1 = pd.read_csv(p1_file)
p2 = pd.read_csv(p2_file)

# Conditions
f_bases = ['F1_0', 'F2_0'] + [f'F_{i}' for i in range(1, 11)]
r_bases = ['R1_0', 'R2_0'] + [f'R_{i}' for i in range(1, 11)]
labels = ['Evo', 'Plate', '0 (1)', '0 (2)'] + [str(i) for i in range(1, 11)]

# Calculate Evo and Plate
evo_mean, evo_se = get_mean_se(p1, 'Evo_1')
plate_mean, plate_se = get_mean_se(p1, 'Plate_1')

# Calculate F and R
f_means, f_ses, r_means, r_ses = [], [], [], []

for base in f_bases:
    df = p2 if base in ['F1_0', 'F2_0'] or int(base.split('_')[1]) <=5 else p1
    mean_count, se_count = get_mean_se(df, base)
    f_means.append(mean_count)
    f_ses.append(se_count)

for base in r_bases:
    df = p2 if base in ['R1_0', 'R2_0'] or int(base.split('_')[1]) <=5 else p1
    mean_count, se_count = get_mean_se(df, base)
    r_means.append(mean_count)
    r_ses.append(se_count)

# Normalize
f_means_percent = [(val / evo_mean) * 100 for val in f_means]
r_means_percent = [(val / evo_mean) * 100 for val in r_means]
f_ses_percent = [(se / evo_mean) * 100 for se in f_ses]
r_ses_percent = [(se / evo_mean) * 100 for se in r_ses]

f_means_plot = [100, (plate_mean / evo_mean) * 100] + f_means_percent
r_means_plot = [0, 0] + r_means_percent
f_ses_plot = [evo_se / evo_mean * 100, plate_se / evo_mean * 100] + f_ses_percent
r_ses_plot = [0, 0] + r_ses_percent

# Colors
total_bars = len(labels)
f_colors = ['rosybrown', 'sienna'] + list(cm.BuGn(np.linspace(0.3, 1.0, total_bars - 2)))
r_colors = ['white', 'white'] + list(cm.Blues(np.linspace(0.3, 1.0, total_bars - 2)))

# Legend
legend_elements = [
    Patch(facecolor='rosybrown', label='Evo'),
    Patch(facecolor='sienna', label='Plate'),
    Patch(facecolor=cm.BuGn(0.7), label='F (BuGn Gradient)'),
    Patch(facecolor=cm.Blues(0.7), label='R (Blues Gradient)')
]

# Plot
fig, ax = plt.subplots(figsize=(16, 6))
x = np.arange(total_bars)
width = 0.4

ax.bar(x - width/2, f_means_plot, width, color=f_colors, zorder=3, yerr=f_ses_plot, capsize=5)
ax.bar(x + width/2, r_means_plot, width, color=r_colors, zorder=3, yerr=r_ses_plot, capsize=5)

ax.yaxis.grid(True, linestyle='--', linewidth=0.5, zorder=0)
ax.set_axisbelow(True)

ax.set_ylabel('%')
ax.set_title('Detection Relative to Evo (%)')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(handles=legend_elements)

plt.tight_layout()
plt.show()
