import pandas as pd
import tkinter as tk
from tkinter import filedialog

# === File Selection ===
root = tk.Tk()
root.withdraw()

print("Select P1 CSV file...")
p1_file = filedialog.askopenfilename(title="Select P1 CSV", filetypes=[("CSV Files", "*.csv")])

print("Select P2 CSV file...")
p2_file = filedialog.askopenfilename(title="Select P2 CSV", filetypes=[("CSV Files", "*.csv")])

print("Select folder to save scaled P2...")
output_dir = filedialog.askdirectory(title="Select Output Folder")

# === Load Data ===
p1 = pd.read_csv(p1_file)
p2 = pd.read_csv(p2_file)

# === Compute Median (No Zeros) Scaling Factors ===
def compute_median_no_zeros(df, condition_prefix):
    reps = [col for col in df.columns if col.startswith(condition_prefix)]
    values = df[reps].values.flatten()
    values_no_zeros = values[values != 0]
    return pd.Series(values_no_zeros).median()

median_f5 = compute_median_no_zeros(p2, 'F_5')
median_f6 = compute_median_no_zeros(p1, 'F_6')
median_r5 = compute_median_no_zeros(p2, 'R_5')
median_r6 = compute_median_no_zeros(p1, 'R_6')

scaling_f = median_f6 / median_f5
scaling_r = median_r6 / median_r5

print(f"F Scaling Factor (Median No Zeros): {scaling_f:.4f}")
print(f"R Scaling Factor (Median No Zeros): {scaling_r:.4f}")

# === Apply Scaling ===
p2_scaled = p2.copy()
for col in p2_scaled.select_dtypes(include='number').columns:
    if col.startswith('F_'):
        p2_scaled[col] *= scaling_f
    elif col.startswith('R_'):
        p2_scaled[col] *= scaling_r

# === Save Scaled P2 ===
output_path = f"{output_dir}/P2_median_scaled_dual.csv"
p2_scaled.to_csv(output_path, index=False)
print(f"✅ Scaled P2 saved to: {output_path}")
