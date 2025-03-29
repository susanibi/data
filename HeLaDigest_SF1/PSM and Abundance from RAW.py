import pandas as pd
import numpy as np
import os
from tkinter import Tk, filedialog
from tqdm import tqdm

# Kyte & Doolittle hydropathy index
hydropathy_index = {
    'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
    'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
    'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
    'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
}


def calculate_gravy(sequence):
    values = [hydropathy_index.get(aa, 0) for aa in sequence]
    return sum(values) / len(values) if values else np.nan

def extract_clean_sample_name(col_path):
    base = os.path.basename(col_path).replace(".raw", "")
    parts = base.split("_")
    if "qc" in base.lower():
        if "exp003" in base.lower():
            return None
        return "qc_50pg_" + parts[-1][-1]
    surface = parts[-4].replace("F", "") if parts[-4].startswith("F") else parts[-4]
    return f"{surface}_{parts[-3]}_{parts[-2]}_{parts[-1][-1]}"

def load_pr_matrix_files(folder):
    pr_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file == "report.pr_matrix.tsv":
                pr_files.append(os.path.join(root, file))
    return pr_files

def bin_gravy_column(gravy_values, bin_size=0.05):
    min_bin = np.floor(min(gravy_values) * 20) / 20
    max_bin = np.ceil(max(gravy_values) * 20) / 20
    bins = np.arange(min_bin, max_bin + bin_size, bin_size)
    labels = [f"{round(bins[i], 3)} to {round(bins[i+1], 3)}" for i in range(len(bins) - 1)]
    return bins, labels

def main():
    root = Tk()
    root.withdraw()
    selected_dir = filedialog.askdirectory(title="Select folder containing PR matrix .tsv files")
    if not selected_dir:
        print("❌ No folder selected.")
        return

    pr_files = load_pr_matrix_files(selected_dir)

    raw_abundance_dict = {}
    gravy_sorted_abundance_dict = {}
    psm_count_dict = {}
    psm_percent_dict = {}
    all_gravy = []

    for pr_file in tqdm(pr_files, desc="Processing .tsv files"):
        df = pd.read_csv(pr_file, sep="\t")
        if 'Stripped.Sequence' not in df.columns:
            continue
        df["GRAVY"] = df["Stripped.Sequence"].apply(calculate_gravy)
        all_gravy.extend(df["GRAVY"].dropna().tolist())

        raw_cols = [col for col in df.columns if col.endswith(".raw")]
        sample_map = {col: extract_clean_sample_name(col) for col in raw_cols}
        sample_map = {k: v for k, v in sample_map.items() if v is not None}
        if not sample_map:
            continue

        df.rename(columns=sample_map, inplace=True)
        samples = list(sample_map.values())
        df["PSM_Like_Count"] = df[samples].notna().sum(axis=1)
        base_name = os.path.basename(os.path.dirname(pr_file))
        raw_abundance_dict[base_name] = df[["Stripped.Sequence", "GRAVY", "Precursor.Charge"] + samples]

    # Bin GRAVY globally
    gravy_bins, gravy_labels = bin_gravy_column(all_gravy)

    # Gravy Binned Abundance and PSM Calculation
    for name, df in raw_abundance_dict.items():
        df["GRAVY_bin"] = pd.cut(df["GRAVY"], bins=gravy_bins, labels=gravy_labels, include_lowest=True)
        data_cols = df.columns[3:-1]
        non_empty_cols = df[data_cols].columns[df[data_cols].notna().any()]
        df = df[["GRAVY_bin"] + list(non_empty_cols)]

        abundance = df.groupby("GRAVY_bin", observed=True)[non_empty_cols].mean()
        gravy_sorted_abundance_dict[name] = abundance.reset_index()

        psm_counts = df.groupby("GRAVY_bin", observed=True)[non_empty_cols].apply(lambda g: g.notna().sum())
        psm_count_dict[name] = psm_counts.reset_index()

        psm_percent = psm_counts.div(psm_counts.sum(axis=0), axis=1) * 100
        psm_percent_dict[name] = psm_percent.reset_index()


    # Summary Stats from Replicate-Level Data

    mean_abundance_records = []
    mean_psm_records = []

    for name, df in raw_abundance_dict.items():
        print(f"\n▶ Starting {name}")

        # Recalculate GRAVY
        df["GRAVY"] = df["Stripped.Sequence"].apply(calculate_gravy)

        # Use global GRAVY bin consistently
        df["GRAVY_bin"] = pd.cut(df["GRAVY"], bins=gravy_bins, labels=gravy_labels, include_lowest=True).astype(str)

        # Drop index if needed
        df = df.reset_index(drop=True)

        # Select valid sample columns (ensure GRAVY_bin is not included)
        sample_cols = df.columns[3:]
        valid_cols = sample_cols[df[sample_cols].notna().any()]
        valid_cols = valid_cols.drop('GRAVY_bin', errors='ignore')  # prevent duplicate GRAVY_bin

        df_filtered = df[["GRAVY_bin"] + list(valid_cols)]
        assert df_filtered.columns.duplicated().sum() == 0, "Duplicate column detected!"

        # Safe groupby
        grouped_abund = df_filtered.groupby("GRAVY_bin", observed=True)
        mean_abund = grouped_abund[valid_cols].apply(lambda x: x.fillna(0).mean(), axis=1)
        sem_abund = grouped_abund[valid_cols].std(ddof=1).fillna(0) / np.sqrt(grouped_abund[valid_cols].count())

        # Safe zero count
        temp = df_filtered.assign(GRAVY_bin_label=df_filtered["GRAVY_bin"])
        zero_count_abund = temp[valid_cols].isna().groupby(temp["GRAVY_bin_label"]).sum().sum(axis=1)

        summary_abund = pd.DataFrame({
            "GRAVY_bin": mean_abund.index,
            f"{name}_Mean": mean_abund.mean(axis=1).values,
            f"{name}_SEM": sem_abund.mean(axis=1).values,
            f"{name}_ZeroCount": zero_count_abund.values
        })
        mean_abundance_records.append(summary_abund)

        # %PSM handling
        if name in psm_percent_dict:
            # Replicate-level %PSM (existing calculation)
            df_replicate_percent = psm_percent_dict[name].set_index("GRAVY_bin")

            # Global-level %PSM (calculated independently from counts)
            df_counts = psm_count_dict[name].set_index("GRAVY_bin")
            total_counts_per_bin = df_counts.sum(axis=1)
            grand_total_counts = total_counts_per_bin.sum()

            mean_psm_global = (total_counts_per_bin / grand_total_counts) * 100
            sem_psm_global = (df_counts.div(df_counts.sum(axis=0), axis=1)
                              .std(axis=1, ddof=1)
                              .div(np.sqrt(df_counts.shape[1])) * 100)

            zero_count_psm_global = df_counts.isna().sum(axis=1)

            # Clearly labeled summary dataframe for global-level %PSM
            summary_psm_global = pd.DataFrame({
                "GRAVY_bin": df_counts.index,
                f"{name}_Global_%PSM_Mean": mean_psm_global.values,
                f"{name}_Global_%PSM_SEM": sem_psm_global.values,
                f"{name}_Global_%PSM_ZeroCount": zero_count_psm_global.values
            })

            mean_psm_records.append(summary_psm_global)

        print(f"✅ Finished {name}")

    # Merge
    from functools import reduce
    df_mean_abundance_all = reduce(lambda left, right: pd.merge(left, right, on="GRAVY_bin", how="outer"), mean_abundance_records)
    df_psm_mean_all = reduce(lambda left, right: pd.merge(left, right, on="GRAVY_bin", how="outer"), mean_psm_records)

    # Save all outputs
    raw_abundance_path = os.path.join(selected_dir, "Output_RAW_Abundance.xlsx")
    gravy_sorted_path = os.path.join(selected_dir, "Output_GravyBinned_Abundance.xlsx")
    psm_path = os.path.join(selected_dir, "Output_Raw_PSM_Counts_and_%PSM.xlsx")
    summary_path = os.path.join(selected_dir, "Output_Combined_Mean_Abundance_and_%PSM.xlsx")

    with pd.ExcelWriter(raw_abundance_path) as writer:
        for name, df in raw_abundance_dict.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)

    with pd.ExcelWriter(gravy_sorted_path) as writer:
        for name, df in gravy_sorted_abundance_dict.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)

    with pd.ExcelWriter(psm_path) as writer:
        for name, df in psm_count_dict.items():
            df.to_excel(writer, sheet_name=f"{name[:27]}_Counts", index=False)
        for name, df in psm_percent_dict.items():
            df.to_excel(writer, sheet_name=f"{name[:27]}_%PSM", index=False)

    with pd.ExcelWriter(summary_path) as writer:
        df_mean_abundance_all.to_excel(writer, sheet_name="Mean_Abundance", index=False)
        df_psm_mean_all.to_excel(writer, sheet_name="Mean_%PSM", index=False)

    # BLOCK: Processing Summary Output
    print("\n📊 Processing Summary:")
    print(f"📁 Selected folder: {selected_dir}")
    print(f"🧾 Total .tsv files found: {len(pr_files)}")
    print(f"📄 Subfolders processed: {len(raw_abundance_dict)}\n")

    for name, df in raw_abundance_dict.items():
        sample_cols = df.columns[3:]
        seq_count = len(df)
        print(f"  ▶ {name}:")
        print(f"     • Sequences: {seq_count}")
        print(f"     • Samples: {len(sample_cols)} -> {', '.join(sample_cols)}")

    print("\n✅ Done. All output files saved.\n")


if __name__ == "__main__":
    main()
