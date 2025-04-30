#!/usr/bin/env python3
import pandas as pd
import numpy as np
import re
import tkinter as tk
from tkinter import filedialog

def main():
    # --- File selection ---
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Select combined P1/P2 peptide file (shared peptides)",
        filetypes=[("CSV files", "*.csv")]
    )
    if not path:
        print("No file selected.")
        return

    # --- Load file ---
    df = pd.read_csv(path)

    # --- Identify replicate columns ---
    rep_cols = [col for col in df.columns if re.match(r".*\.\d+$", col)]

    # --- Group by sample group prefix (e.g. F_1 from F_1.1, F_1.2...) ---
    group_map = {col: col.rsplit('.', 1)[0] for col in rep_cols}
    groups = sorted(set(group_map.values()))

    # --- Apply filtering: set all values to NaN if < 3 replicates detected ---
    df_filtered = df.copy()
    for group in groups:
        group_reps = [col for col in rep_cols if group_map[col] == group]
        detected = df_filtered[group_reps].notna().sum(axis=1)
        low_confidence = detected < 3
        df_filtered.loc[low_confidence, group_reps] = np.nan

    # --- Log2 transform (after filtering, skipping 0s) ---
    df_log2 = df_filtered.copy()
    df_log2[rep_cols] = df_log2[rep_cols].replace(0, np.nan)
    df_log2[rep_cols] = np.log2(df_log2[rep_cols])

    # --- Median normalization per replicate ---
    df_normalized = df_log2.copy()
    df_normalized[rep_cols] = df_log2[rep_cols].sub(df_log2[rep_cols].median(), axis=1)

    # --- Save output ---
    output_path = path.replace(".csv", "_filtered_log2_normalized.csv")
    df_normalized.to_csv(output_path, index=False)
    print(f"Saved cleaned and normalized file to:\n{output_path}")

if __name__ == "__main__":
    main()
