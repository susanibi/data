import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from tkinter import Tk, filedialog

# Kyte & Doolittle hydropathy index
hydropathy_index = {
    'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
    'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
    'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
    'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
}

def calculate_gravy(sequence):
    aa_values = [hydropathy_index.get(aa, 0) for aa in sequence]
    return sum(aa_values) / len(sequence) if sequence else np.nan

def find_pr_matrix_files(root_folder):
    pr_files = []
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename == "report.pr_matrix.tsv":
                pr_files.append(os.path.join(dirpath, filename))
    return pr_files

def extract_experiment_tag(path):
    parts = path.lower().split('_')
    for part in parts:
        if part.startswith('exp'):
            return part
    return "noexp"

def shorten_sample_name(path):
    base = os.path.basename(path)
    if base.endswith('.raw'):
        base = base.replace('.raw', '')
    parts = base.lower().split('_')
    exp = extract_experiment_tag(base)
    short_name = '_'.join(parts[-3:])
    return f"{exp}_{short_name}"

def analyze_gravy_psm():
    root = Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(title="Select parent folder containing report.pr_matrix.tsv files")
    if not folder_path:
        print("No folder selected.")
        return

    pr_files = find_pr_matrix_files(folder_path)
    if not pr_files:
        print("No 'report.pr_matrix.tsv' files found.")
        return

    peptide_psm_summary = {}
    gravy_sample_psm_summary = {}
    gravy_abundance_summary = {}
    all_gravy = []

    for file_path in tqdm(pr_files, desc="Processing files"):
        try:
            df = pd.read_csv(file_path, sep='\t')
            if 'Stripped.Sequence' not in df.columns:
                continue

            df["GRAVY"] = df["Stripped.Sequence"].apply(calculate_gravy)

            # Identify and rename sample columns
            sample_cols_raw = [col for col in df.columns if col.endswith(".raw")]
            short_name_map = {col: shorten_sample_name(col) for col in sample_cols_raw}

            # Filter out Exp003 samples
            short_name_map = {orig: short for orig, short in short_name_map.items() if not short.startswith("exp003")}
            df.rename(columns=short_name_map, inplace=True)

            # New list of sample columns, excluding Exp003
            sample_cols = list(short_name_map.values())

            # Identify QC samples from Exp002
            qc_exp002_cols = [col for col in sample_cols if "qc" in col and "exp002" in col]

            # Save GRAVY values
            all_gravy.extend(df["GRAVY"].dropna().tolist())

            df["PSM_Like_Count"] = df[sample_cols].notna().sum(axis=1)
            subfolder_name = os.path.basename(os.path.dirname(file_path))

            df = df[["GRAVY", "PSM_Like_Count"] + sample_cols].copy()
            peptide_psm_summary[subfolder_name] = (df, sample_cols, qc_exp002_cols)
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Global GRAVY bins
    min_gravy = np.floor(min(all_gravy) * 20) / 20
    max_gravy = np.ceil(max(all_gravy) * 20) / 20
    bins = np.arange(min_gravy, max_gravy + 0.05, 0.05)
    bin_labels = [f"{round(bins[i], 3)} to {round(bins[i+1], 3)}" for i in range(len(bins) - 1)]

    for name, (df, sample_cols, qc_exp002_cols) in peptide_psm_summary.items():
        df["GRAVY_bin"] = pd.cut(df["GRAVY"], bins=bins, labels=bin_labels, include_lowest=True)

        # Summary: %PSM-like per peptide
        count_per_bin = df.groupby("GRAVY_bin", observed=False).size().rename("Peptide_Count")
        percent_peptides = count_per_bin / count_per_bin.sum() * 100
        mean_psm_per_bin = df.groupby("GRAVY_bin", observed=False)["PSM_Like_Count"].mean()
        psm_summary = pd.concat([
            count_per_bin, percent_peptides.rename("%Peptides"),
            mean_psm_per_bin.rename("Mean_PSM_Per_Peptide")
        ], axis=1).reset_index()
        peptide_psm_summary[name] = psm_summary

        # Total PSMs per bin, per replicate
        summed_psm = df.groupby("GRAVY_bin", observed=False)[sample_cols].apply(lambda g: g.notna().sum())
        gravy_sample_psm_summary[name] = summed_psm.reset_index()

        # Mean abundance per bin
        mean_abund = df.groupby("GRAVY_bin", observed=False)[sample_cols].mean()
        gravy_abundance_summary[name] = mean_abund.reset_index()

    # Save Excel outputs
    output_files = {
        "PSM_Per_Peptide_Per_Gravy.xlsx": peptide_psm_summary,
        "PSM_Per_Gravy_Per_Sample.xlsx": gravy_sample_psm_summary,
        "Mean_Abundance_Per_Gravy.xlsx": gravy_abundance_summary,
    }

    for filename, data_dict in output_files.items():
        save_path = filedialog.asksaveasfilename(
            title=f"Save output for {filename}",
            initialfile=filename,
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if save_path:
            with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
                for sheet_name, df in data_dict.items():
                    df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
            print(f"✅ Saved: {save_path}")
        else:
            print(f"⚠️ Skipped saving for {filename}")

if __name__ == "__main__":
    analyze_gravy_psm()
