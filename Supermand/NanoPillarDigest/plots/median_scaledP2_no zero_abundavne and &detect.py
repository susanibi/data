import pandas as pd
import matplotlib.pyplot as plt





# === Load Data ===
df = pd.read_csv('Condition_Median_and_Detection_Summary.csv')

# === Prepare Data ===
f_data = df[df['Material'] == 'F'].sort_values('Roughness')
r_data = df[df['Material'] == 'R'].sort_values('Roughness')

# === Plot ===
fig, ax1 = plt.subplots(figsize=(12, 6))

# Plot Median Intensity (Solid Lines)
ax1.plot(f_data['Roughness'], f_data['Median (No Zeros)'], color='green', marker='o', linestyle='-', label='F Median')
ax1.plot(r_data['Roughness'], r_data['Median (No Zeros)'], color='blue', marker='s', linestyle='-', label='R Median')
ax1.set_xlabel('Surface Roughness Level')
ax1.set_ylabel('Median Peptide Intensity (No Zeros)')
ax1.grid(True, axis='y')

# Secondary Axis for % Detected
ax2 = ax1.twinx()
ax2.plot(f_data['Roughness'], f_data['% Peptides Detected'], color='green', marker='o', linestyle='--', label='F % Detected')
ax2.plot(r_data['Roughness'], r_data['% Peptides Detected'], color='blue', marker='s', linestyle='--', label='R % Detected')
ax2.set_ylabel('% Peptides Detected')
ax2.set_ylim(0, 100)

# Combine Legends
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

plt.title('Median Intensity (Solid) and % Detected (Dashed) Across Roughness')
plt.tight_layout()
plt.show()
