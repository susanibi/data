#!/usr/bin/env python3
import pandas as pd
import numpy as np
import re
import os
import tkinter as tk
from tkinter import filedialog

def main():
    # GUI: Select input file
    root = tk.Tk()
    root.withdraw()
    input_path = filedialog.askopenfilename(
        title="Select merged peptide intensity CSV",
        filetypes=[("CSV files", "*.csv")]
    )
    if not input_path:
        print("No file selected.")
        return

    # GUI: Select output folder
    output_dir = filedialog.askdirectory(title="Select folder to save output files")
    if not output_dir:
        print("No output folder selected.")
        return

    # Load data
    df = pd.read_csv(input_path, index_col=0).replace(0, np.nan)
    if "GravyScore" not in df.columns:
        print("Missing 'GravyScore' column.")
        return

    gravy = df["GravyScore"]
    rep_cols = [col for col in df.columns if re.match(r".*\.\d+$", col)]
    df_reps = df[rep_cols].copy()

    # Map replicates to group names
    group_map = {col: col.rsplit(".", 1)[0] for col in rep_cols}
    df_long = df_reps.stack().reset_index()
    df_long.columns = ["peptide", "replicate", "intensity"]
    df_long["sample"] = df_long["replicate"].map(group_map)
    df_long["GravyScore"] = df_long["peptide"].map(gravy)

    # Identify dataset from replicate naming
    def get_dataset(sample):
        return "P1" if sample.startswith("F_") or sample.startswith("R_") else "P2"
    df_long["dataset"] = df_long["sample"].apply(get_dataset)

    # Find shared peptides: detected in at least 1 replicate in both P1 and P2
    detected = df_long.dropna(subset=["intensity"])
    dataset_presence = detected.groupby(["peptide", "dataset"]).size().unstack(fill_value=0)
    shared_peptides = dataset_presence[(dataset_presence["P1"] > 0) & (dataset_presence["P2"] > 0)].index

    # Filter to shared peptides only
    df_long = df_long[df_long["peptide"].isin(shared_peptides)]

    # Filter peptide × sample groups with <3 replicates
    rep_counts = df_long.groupby(["peptide", "sample"])["intensity"].apply(lambda x: x.notna().sum())
    keep = rep_counts[rep_counts >= 3].index
    df_long.loc[~df_long.set_index(["peptide", "sample"]).index.isin(keep), "intensity"] = np.nan

    # NEW: Remove peptides with no valid values in any group
    valid_peptides = df_long.dropna(subset=["intensity"])["peptide"].unique()
    df_long = df_long[df_long["peptide"].isin(valid_peptides)]

    # Save filtered long-form replicate-level data
    filtered_path = os.path.join(output_dir, "filtered_replicate_level.csv")
    df_long.to_csv(filtered_path, index=False)
    print(f"Saved replicate-level data: {filtered_path}")

    # Compute group-level summary: median and IQR
    summary = (
        df_long.groupby(["peptide", "sample"])["intensity"]
        .agg(median="median", IQR=lambda x: np.nanpercentile(x, 75) - np.nanpercentile(x, 25))
        .reset_index()
        .pivot(index="peptide", columns="sample")
    )
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary["GravyScore"] = df_long.drop_duplicates("peptide").set_index("peptide")["GravyScore"]

    summary_path = os.path.join(output_dir, "group_medians_iqr.csv")
    summary.to_csv(summary_path)
    print(f"Saved group-level summary: {summary_path}")

    # Log2 transform and median normalize the medians
    med_cols = [col for col in summary.columns if col.startswith("median_")]
    df_log = np.log2(summary[med_cols])
    df_norm = df_log.sub(df_log.median(axis=0), axis=1)
    df_final = pd.concat([df_norm, summary[["GravyScore"]]], axis=1)

    norm_path = os.path.join(output_dir, "group_medians_log2norm.csv")
    df_final.to_csv(norm_path)
    print(f"Saved log2-normalized summary: {norm_path}")

if __name__ == "__main__":
    main()
