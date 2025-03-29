#This script locates Pr_Matrix TSV file in subfolder from a chosen parent folder
#it extracts seq.protId,precursor, sample ID etc., and insert a column with calculated gravy score
#for the stripped.sequences. It makes a new sheet for each subfolder


import pandas as pd
import numpy as np
import os
from tkinter import Tk, filedialog

# Kyte & Doolittle hydropathy index
hydropathy_index = {
    'A': 1.8,  'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
    'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
    'L': 3.8,  'K': -3.9, 'M': 1.9,  'F': 2.8,  'P': -1.6,
    'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
}

def calculate_gravy(sequence):
    aa_values = [hydropathy_index.get(aa, 0) for aa in sequence]
    return sum(aa_values) / len(sequence) if sequence else np.nan

def find_pr_matrix_files(root_folder):
    pr_files = []
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename == "report.pr_matrix" or filename == "report.pr_matrix.tsv":
                pr_files.append(os.path.join(dirpath, filename))
    return pr_files

def process_all_pr_matrices():
    root = Tk()
    root.withdraw()

    # Choose root folder
    folder_path = filedialog.askdirectory(title="Select the parent folder containing pr_matrix files")
    if not folder_path:
        print("No folder selected.")
        return

    pr_files = find_pr_matrix_files(folder_path)
    if not pr_files:
        print("No 'report.pr_matrix' files found in the folder or subfolders.")
        return

    output_data = {}

    for file_path in pr_files:
        try:
            df = pd.read_csv(file_path, sep="\t")

            if "Stripped.Sequence" not in df.columns:
                print(f"Skipping {file_path} — 'Stripped.Sequence' column not found.")
                continue

            df["GRAVY"] = df["Stripped.Sequence"].apply(calculate_gravy)
            cols = ["Stripped.Sequence", "GRAVY"] + [col for col in df.columns if col not in ["Stripped.Sequence", "GRAVY"]]
            df = df[cols]

            # Use the immediate subfolder name as sheet name
            subfolder_name = os.path.basename(os.path.dirname(file_path))

            # Avoid duplicate sheet names
            if subfolder_name in output_data:
                suffix = 1
                new_name = f"{subfolder_name}_{suffix}"
                while new_name in output_data:
                    suffix += 1
                    new_name = f"{subfolder_name}_{suffix}"
                subfolder_name = new_name

            output_data[subfolder_name] = df
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    if not output_data:
        print("No valid data to write.")
        return

    save_path = filedialog.asksaveasfilename(
        title="Save Excel file with GRAVY scores",
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx")]
    )
    if save_path:
        with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
            for sheet_name, df in output_data.items():
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)  # Excel sheet names max length = 31
        print(f"✅ Excel file saved: {save_path}")
    else:
        print("No output file saved.")

if __name__ == "__main__":
    process_all_pr_matrices()
