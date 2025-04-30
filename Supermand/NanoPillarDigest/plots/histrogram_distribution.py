import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
import tkinter as tk

# ====== USER SETTINGS ======
p1_color = 'purple'   # Soft warm yellow / light gold
p2_color = 'orange'   # Soft peachy orange
font_size = 14
bins_number = 50
alpha_value = 0.5
# ===========================

plt.rcParams['font.size'] = font_size

def load_group_data(file_path, group_type):
    df = pd.read_csv(file_path)
    if group_type == 'P2':
        prefixes = [f"{prefix}_{i}" for prefix in ['F', 'R'] for i in range(1, 6)]
        extras = ['F1_', 'F2_', 'R1_', 'R2_']
        selected_cols = [col for col in df.columns if any(col.startswith(p) for p in prefixes + extras)]
    elif group_type == 'P1':
        prefixes = [f"{prefix}_{i}" for prefix in ['F', 'R'] for i in range(6, 11)]
        selected_cols = [col for col in df.columns if any(col.startswith(p) for p in prefixes)]
    else:
        return pd.Series([])

    data_long = df[selected_cols].melt(var_name='Sample', value_name='Intensity')
    data_nonzero = data_long[data_long['Intensity'] > 0]['Intensity']
    data_log2 = np.log2(data_nonzero)
    return data_log2

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    print("Select P1 and P2 CSV files...")
    file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])

    if file_paths and len(file_paths) == 2:
        p1_file, p2_file = file_paths

        p1_log2 = load_group_data(p1_file, 'P1')
        p2_log2 = load_group_data(p2_file, 'P2')

        fig, ax = plt.subplots(figsize=(10,6))
        ax.hist(p1_log2, bins=bins_number, alpha=alpha_value, label='P1', density=True, color=p1_color)
        ax.hist(p2_log2, bins=bins_number, alpha=alpha_value, label='P2', density=True, color=p2_color)
        ax.set_xlabel('Peptide Intensity (log2)')
        ax.set_ylabel('Density')
        ax.set_title('Peptide Intensity Distributions')
        ax.legend()
        ax.grid(True)
        ax.set_axisbelow(True)
        plt.show()

    else:
        print("Please select exactly two files (P1 and P2 datasets). Exiting.")
