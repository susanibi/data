#This scrtip used GRAVY_sort output, to bin gravyscore, count the number of peptides in a bin
#and give the mean abundance per sample per bin.

import pandas as pd
import numpy as np
from tkinter import Tk, filedialog
from tqdm import tqdm  # progress bar!

def bin_and_summarize_gravy():
    # Hide the main tkinter window
    root = Tk()
    root.withdraw()

    # Let user select the GRAVY-sorted Excel file
    input_path = filedialog.askopenfilename(
        title="Select GRAVY-sorted Excel file",
        filetypes=[("Excel Files", "*.xlsx")]
    )
    if not input_path:
        print("No file selected.")
        return

    # Load all sheets
    xls = pd.ExcelFile(input_path)
    all_gravy_values = []
    sheet_dfs = {}

    # Load all GRAVY values for binning + filter relevant columns
    for sheet_name in xls.sheet_names:
        df = xls.parse(sheet_name)
        if "GRAVY" not in df.columns:
            continue
        # Identify sample ID columns: keep only GRAVY + sample columns
        sample_cols = [col for col in df.columns if col != 'GRAVY' and not any(x in col for x in [
            'Stripped.Sequence', 'Protein.Group', 'Precursor.Charge', 'Genes',
            'Proteotypic', 'Precursor.Id'
        ])]
        filtered_df = df[['GRAVY'] + sample_cols].copy()
        sheet_dfs[sheet_name] = filtered_df
        all_gravy_values.extend(filtered_df['GRAVY'].dropna().tolist())

    if not sheet_dfs:
        print("No valid sheets found.")
        return

    # Create global GRAVY bins (0.05 width)
    min_gravy = np.floor(min(all_gravy_values) * 20) / 20
    max_gravy = np.ceil(max(all_gravy_values) * 20) / 20
    bins = np.arange(min_gravy, max_gravy + 0.05, 0.05)
    bin_labels = [f"{round(bins[i], 3)} to {round(bins[i+1], 3)}" for i in range(len(bins) - 1)]

    # Process each sheet with a progress bar
    output_data = {}
    for sheet_name in tqdm(sheet_dfs, desc="Processing Sheets"):
        df = sheet_dfs[sheet_name].copy()
        df["GRAVY_bin"] = pd.cut(df["GRAVY"], bins=bins, labels=bin_labels, include_lowest=True)

        # Sample ID columns (i.e., all except GRAVY and GRAVY_bin)
        sample_cols = [col for col in df.columns if col not in ['GRAVY', 'GRAVY_bin']]

        # Group by GRAVY bin
        grouped = df.groupby("GRAVY_bin", observed=False)
        count_series = grouped.size().rename("Peptide_Count")
        mean_abundance = grouped[sample_cols].mean(numeric_only=True)

        summary_df = pd.concat([count_series, mean_abundance], axis=1).reset_index()
        output_data[sheet_name] = summary_df

    # Save the result
    save_path = filedialog.asksaveasfilename(
        title="Save GRAVY bin summary file",
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx")]
    )

    if save_path:
        with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
            for sheet_name, df in output_data.items():
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        print(f"✅ GRAVY binned summary saved to: {save_path}")
    else:
        print("No output file saved.")

if __name__ == "__main__":
    bin_and_summarize_gravy()
