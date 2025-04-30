#!/usr/bin/env python3
import pandas as pd
import re
import tkinter as tk
from tkinter import filedialog

def calculate_missingness(df):
    # Ensure GRAVY score is present
    if "GravyScore" not in df.columns:
        raise ValueError("Missing 'GravyScore' column.")

    gravy = df["GravyScore"]

    # Identify replicate columns (e.g., F_1.1, R1_0.2)
    rep_cols = [c for c in df.columns if re.match(r".*\.\d+$", c)]
    if not rep_cols:
        raise ValueError("No replicate columns matched pattern 'name.number'.")

    # Map replicates to method/sample group
    meta = pd.DataFrame({
        "replicate": rep_cols,
        "method": [c.rsplit(".", 1)[0] for c in rep_cols]
    })

    # Build missingness matrix (1 = missing, 0 = present)
    M = df[rep_cols].replace(0, pd.NA).isna().astype(int)

    # Melt to long form
    M_long = M.stack(dropna=False).reset_index()
    M_long.columns = ["peptide", "replicate", "is_missing"]
    M_long = M_long.merge(meta, on="replicate")

    # Compute missingness rate per peptide × method
    rates = (
        M_long
        .groupby(["peptide", "method"])["is_missing"]
        .mean()
        .unstack(fill_value=0)
    )

    # Merge back GRAVY score
    rates = rates.merge(gravy, left_index=True, right_index=True)

    return rates


def bin_missingness(df, bins=20):
    # Drop rows without GRAVY scores
    df = df.dropna(subset=['GravyScore'])

    # Bin GRAVY scores
    df['GravyBin'] = pd.cut(df['GravyScore'], bins=bins)

    # Keep only numeric columns (sample groups)
    sample_cols = df.select_dtypes(include='number').columns.difference(['GravyScore'])

    # Group and compute mean missingness
    summary = df.groupby('GravyBin', observed=True)[sample_cols].mean().reset_index()
    return summary


def main():
    # GUI file dialog setup
    root = tk.Tk()
    root.withdraw()

    input_file = filedialog.askopenfilename(
        title="Select merged peptide intensity CSV",
        filetypes=[("CSV files", "*.csv")]
    )
    if not input_file:
        print("No file selected. Exiting.")
        return

    df = pd.read_csv(input_file, index_col=0)

    try:
        # Calculate missingness
        missingness_df = calculate_missingness(df)
        out1 = input_file.replace(".csv", "_missingness_rates_with_gravy.csv")
        missingness_df.to_csv(out1)
        print(f"Saved peptide-level missingness matrix: {out1}")

        # Bin by GRAVY and aggregate
        binned_df = bin_missingness(missingness_df, bins=20)
        out2 = input_file.replace(".csv", "_binned_missingness.csv")
        binned_df.to_csv(out2, index=False)
        print(f"Saved GRAVY-binned missingness summary: {out2}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
