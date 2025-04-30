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

# === Compute Mean-Based Scaling Factors ===
def compute_mean(df, condition_prefix):
    reps = [col for col in df.columns if col.startswith(condition_prefix)]
    return df[reps].values.flatten().mean()

mean_f5 = compute_mean(p2, 'F_5')
mean_f6 = compute_mean(p1, 'F_6')
mean_r5 = compute_mean(p2, 'R_5')
mean_r6 = compute_mean(p1, 'R_6')

scaling_f = mean_f6 / mean_f5
scaling_r = mean_r6 / mean_r5

print(f"F Scaling Factor (Mean): {scaling_f:.4f}")
print(f"R Scaling Factor (Mean): {scaling_r:.4f}")

# === Apply Scaling ===
p2_scaled = p2.copy()
for col in p2_scaled.select_dtypes(include='number').columns:
    if col.startswith('F_'):
        p2_scaled[col] *= scaling_f
    elif col.startswith('R_'):
        p2_scaled[col] *= scaling_r

# === Save Scaled P2 ===
output_path = f"{output_dir}/P2_mean_scaled_dual.csv"
p2_scaled.to_csv(output_path, index=False)
print(f"✅ Scaled P2 saved to: {output_path}")
