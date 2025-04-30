
import matplotlib.pyplot as plt
import numpy as np

# Hardcoded data
conditions = ['Plate_1', 'F1_0', 'F2_0', 'F_3', 'F_2', 'F_5', 'F_4', 'F_9', 'F_10', 'F_8', 'F_6', 'F_1',
              'R1_0', 'R2_0', 'R_4', 'R_3', 'R_2', 'R_5', 'R_7', 'R_9', 'R_8', 'R_6', 'R_10', 'R_1']
percent_recovery = [92.08, 49.18, 27.01, 11.67, 18.29, 18.25, 21.34, 25.75, 16.06, 22.77, 18.25, 31.17,
                    33.27, 18.65, 10.21, 3.59, 3.99, 11.86, 18.63, 17.99, 21.00, 11.86, 24.35, 6.69]

# Prepare gradient sizes
f_total = 12  # F1, F2, F_1 to F_10
r_total = 12  # R1, R2, R_1 to R_10

# Create color gradients following plotting order
f_gradient = plt.cm.BuGn(np.linspace(0.3, 1, f_total))
r_gradient = plt.cm.Blues(np.linspace(0.3, 1, r_total))

# Assign colors dynamically
colors = []
f_count = 0
r_count = 0

for cond in conditions:
    if cond.startswith(('F_', 'F1_', 'F2_')):
        colors.append(f_gradient[f_count])
        f_count += 1
    elif cond.startswith(('R_', 'R1_', 'R2_')):
        colors.append(r_gradient[r_count])
        r_count += 1
    elif cond.startswith('Plate'):
        colors.append('#B5695A')  # red-brown for Plate
    else:
        colors.append('#999999')

# Clean labels
labels = [c.replace('_0', '').replace('Plate_1', 'Plate') for c in conditions]

# Plot
plt.figure(figsize=(16, 6))
plt.bar(labels, percent_recovery, color=colors)
plt.axhline(100, color='grey', linestyle='--', linewidth=1)
plt.ylabel('% Recovery')
plt.title('% Recovery Compared to Evo')
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y')
plt.gca().set_axisbelow(True)
plt.tight_layout()
plt.show()
