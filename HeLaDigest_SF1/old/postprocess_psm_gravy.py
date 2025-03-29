import pandas as pd
import numpy as np
from tkinter import Tk, filedialog
from openpyxl import load_workbook

def get_lower_bound(bin_label):
    return float(str(bin_label).split()[0])

def load_excel_with_all_sheets(path):
    xls = pd.ExcelFile(path)
    return {sheet: xls.parse(sheet) for sheet in xls.sheet_names}

def clean_sample_name(name):
    return name.replace("002_", "").replace("exp002_", "")

def compute_qc_total(psm_sheets):
    if "QC" not in psm_sheets:
        return None
    df = psm_sheets["QC"]
    qc_cols = [col for col in df.columns if "qc" in col.lower()]
    return df[qc_cols].sum().sum()

def merge_on_gravy_bin(dfs):
    merged = None
    for df in dfs:
        if merged is None:
            merged = df
        else:
            merged = pd.merge(merged, df, on="GRAVY_bin_LB", how="outer")
    return merged.sort_values("GRAVY_bin_LB")

def process_psm_per_sample(psm_sheets):
    all_avg = []
    all_individual = []
    all_qc_norm = []

    qc_total = compute_qc_total(psm_sheets)

    for sheet, df in psm_sheets.items():
        if "GRAVY_bin" not in df.columns:
            continue

        gravy_col = df["GRAVY_bin"]
        data = df.drop(columns=["GRAVY_bin"]).copy()
        data.columns = [clean_sample_name(c) for c in data.columns]

        # ✅ Fix: Compute %PSM per sample first (per column)
        data_percent = data.div(data.sum(axis=0), axis=1) * 100

        # Then average those percentages across replicates
        avg_percent = data_percent.mean(axis=1)

        # Also compute average PSM count per bin (for reference)
        avg_raw_psm = data.mean(axis=1)

        df_out = pd.DataFrame({
            "GRAVY_bin": gravy_col,
            "Avg_PSM": avg_raw_psm,
            "%Total_PSM_This_Exp": avg_percent.round(2)
        })

        if qc_total:
            df_out["%Total_PSM_QC_Normalized"] = (avg_raw_psm / qc_total * 100).round(2)

        df_out["GRAVY_bin_LB"] = df_out["GRAVY_bin"].apply(get_lower_bound)

        all_avg.append(df_out[["GRAVY_bin_LB", "Avg_PSM"]].rename(columns={"Avg_PSM": sheet}))
        all_individual.append(df_out[["GRAVY_bin_LB", "%Total_PSM_This_Exp"]].rename(columns={"%Total_PSM_This_Exp": sheet}))

        if qc_total:
            all_qc_norm.append(df_out[["GRAVY_bin_LB", "%Total_PSM_QC_Normalized"]].rename(columns={"%Total_PSM_QC_Normalized": sheet}))

        psm_sheets[sheet] = df_out.drop(columns="GRAVY_bin_LB")

    combined = {
        "ALL_AVG": merge_on_gravy_bin(all_avg),
        "ALL_%PSM_Individual": merge_on_gravy_bin(all_individual),
    }
    if all_qc_norm:
        combined["ALL_%PSM_QCnormalized"] = merge_on_gravy_bin(all_qc_norm)
    return combined

# --- UNCHANGED: ABUNDANCE SECTION ---

def process_mean_abundance(abundance_sheets):
    all_mean = []
    all_sem_std = []
    all_sem_incl0 = []
    all_zero_counts = []

    for sheet, df in abundance_sheets.items():
        if "GRAVY_bin" not in df.columns:
            continue

        gravy_col = df["GRAVY_bin"]
        data = df.drop(columns=["GRAVY_bin"])
        data.columns = [clean_sample_name(c) for c in data.columns]

        avg = data.mean(axis=1)
        sem_std = data.sem(axis=1)
        sem_incl0 = data.fillna(0).std(axis=1, ddof=1) / np.sqrt(data.shape[1])
        count_zeros = data.isna().sum(axis=1)

        df_out = pd.DataFrame({
            "GRAVY_bin": gravy_col,
            "Mean_Abundance": avg,
            "SEM_Abundance": sem_std,
            "SEM_Abundance_incl0": sem_incl0,
            "Zero_Count": count_zeros
        })
        df_out["GRAVY_bin_LB"] = df_out["GRAVY_bin"].apply(get_lower_bound)

        all_mean.append(df_out[["GRAVY_bin_LB", "Mean_Abundance"]].rename(columns={"Mean_Abundance": f"{sheet}_Mean"}))
        all_sem_std.append(df_out[["GRAVY_bin_LB", "SEM_Abundance"]].rename(columns={"SEM_Abundance": f"{sheet}_SEM"}))
        all_sem_incl0.append(df_out[["GRAVY_bin_LB", "SEM_Abundance_incl0"]].rename(columns={"SEM_Abundance_incl0": f"{sheet}_SEM_incl0"}))
        all_zero_counts.append(df_out[["GRAVY_bin_LB", "Zero_Count"]].rename(columns={"Zero_Count": f"{sheet}_ZeroCount"}))

        abundance_sheets[sheet] = df_out.drop(columns="GRAVY_bin_LB")

    merged = merge_on_gravy_bin(all_mean)
    merged = merged.merge(merge_on_gravy_bin(all_sem_std), on="GRAVY_bin_LB", how="outer")
    merged = merged.merge(merge_on_gravy_bin(all_sem_incl0), on="GRAVY_bin_LB", how="outer")
    merged = merged.merge(merge_on_gravy_bin(all_zero_counts), on="GRAVY_bin_LB", how="outer")

    return {"ALL_MeanAbundance": merged}

def save_combined_output(output_path, all_data):
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for name, df in all_data.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    print(f"✅ Created new COMBINED file: {output_path}")

def main():
    root = Tk()
    root.withdraw()

    print("📂 Select the PSM file")
    psm_path = filedialog.askopenfilename(title="Select PSM_Per_Gravy_Per_Sample.xlsx")

    print("📂 Select the Mean Abundance file")
    abundance_path = filedialog.askopenfilename(title="Select Mean_Abundance_Per_Gravy.xlsx")

    if not psm_path or not abundance_path:
        print("❌ No files selected. Exiting.")
        return

    import os
    psm_dir = os.path.dirname(psm_path)
    output_path = os.path.join(psm_dir, "COMBINED_abundance_PSM_ALL_new.xlsx")

    psm_sheets = load_excel_with_all_sheets(psm_path)
    abundance_sheets = load_excel_with_all_sheets(abundance_path)

    psm_combined = process_psm_per_sample(psm_sheets)
    abundance_combined = process_mean_abundance(abundance_sheets)

    all_combined = {**psm_combined, **abundance_combined}
    save_combined_output(output_path, all_combined)

if __name__ == "__main__":
    main()
