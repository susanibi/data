
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os

def process_task_a(df, use_metadata=True):
    metadata_cols = ['Modified.Sequence', 'GravySequence', 'GravyScore', 'Precursor.Charge'] if use_metadata else []
    sample_cols = [col for col in df.columns if col not in metadata_cols]
    conditions = set(col.split('.')[0] for col in sample_cols)

    collapsed_data = []

    for condition in conditions:
        replicate_cols = [col for col in sample_cols if col.startswith(condition)]
        mean_values = df[replicate_cols].mean(axis=1)
        detected_counts = (df[replicate_cols] > 0).sum(axis=1)
        percent_detected = (detected_counts / len(replicate_cols)) * 100

        temp_df = df[metadata_cols].copy() if use_metadata else pd.DataFrame()
        temp_df['Condition'] = condition
        temp_df['Mean_Abundance'] = mean_values
        temp_df['Percent_Detected'] = percent_detected

        collapsed_data.append(temp_df)

    collapsed_df = pd.concat(collapsed_data, ignore_index=True)
    return collapsed_df

def process_task_b(df_list):
    stats_data = []
    for df in df_list:
        sample_cols = [col for col in df.columns if col not in ['Modified.Sequence', 'GravySequence', 'GravyScore', 'Precursor.Charge']]
        conditions = set(col.split('.')[0] for col in sample_cols)

        for condition in conditions:
            replicate_cols = [col for col in sample_cols if col.startswith(condition)]
            all_values = df[replicate_cols].values.flatten()
            mean_all = np.mean(all_values)
            std_all = np.std(all_values)
            sem_all = std_all / np.sqrt(len(all_values))

            non_zero_values = all_values[all_values > 0]
            median = np.median(non_zero_values)
            q1 = np.percentile(non_zero_values, 25)
            q3 = np.percentile(non_zero_values, 75)

            stats_data.append({
                'Condition': condition,
                'Global_Mean': mean_all,
                'Std_Dev': std_all,
                'Std_Error': sem_all,
                'Median_NoZero': median,
                'Q1_NoZero': q1,
                'Q3_NoZero': q3
            })

    stats_df = pd.DataFrame(stats_data)
    return stats_df

def process_task_c(df, use_metadata=True):
    metadata_cols = ['Modified.Sequence', 'GravySequence', 'GravyScore', 'Precursor.Charge'] if use_metadata else []
    sample_cols = [col for col in df.columns if col not in metadata_cols]
    conditions = set(col.split('.')[0] for col in sample_cols)

    collapsed_data = []

    for condition in conditions:
        replicate_cols = [col for col in sample_cols if col.startswith(condition)]
        data = df[replicate_cols].replace(0, np.nan)
        median_values = data.median(axis=1, skipna=True)
        q1_values = data.quantile(0.25, axis=1)
        q3_values = data.quantile(0.75, axis=1)
        detected_counts = data.notna().sum(axis=1)
        percent_detected = (detected_counts / len(replicate_cols)) * 100

        temp_df = df[metadata_cols].copy() if use_metadata else pd.DataFrame()
        temp_df['Condition'] = condition
        temp_df['Median_Abundance'] = median_values
        temp_df['Q1'] = q1_values
        temp_df['Q3'] = q3_values
        temp_df['Percent_Detected'] = percent_detected

        collapsed_data.append(temp_df)

    collapsed_df = pd.concat(collapsed_data, ignore_index=True)
    return collapsed_df

def process_task_d(df_list):
    stats_data = []
    for df in df_list:
        sample_cols = [col for col in df.columns if col not in ['Modified.Sequence', 'GravySequence', 'GravyScore', 'Precursor.Charge']]
        conditions = set(col.split('.')[0] for col in sample_cols)

        for condition in conditions:
            replicate_cols = [col for col in sample_cols if col.startswith(condition)]
            data = df[replicate_cols].replace(0, np.nan).values.flatten()
            median = np.nanmedian(data)
            q1 = np.nanpercentile(data, 25)
            q3 = np.nanpercentile(data, 75)
            count_detected = np.sum(~np.isnan(data))

            stats_data.append({
                'Condition': condition,
                'Global_Median': median,
                'Q1': q1,
                'Q3': q3,
                'Detected_Count': count_detected
            })

    stats_df = pd.DataFrame(stats_data)
    return stats_df

def process_task_e_fixed(df, dataset_name, output_folder):
    metadata_cols = ['Modified.Sequence', 'GravySequence', 'GravyScore', 'Precursor.Charge']
    sample_cols = [col for col in df.columns if col not in metadata_cols]
    conditions = set(col.split('.')[0] for col in sample_cols)

    summary = []
    filtered_df = df.copy()
    total_peptides = len(df)

    for condition in conditions:
        replicate_cols = [col for col in sample_cols if col.startswith(condition)]
        zero_counts = (df[replicate_cols] == 0).sum(axis=1)
        to_nan = zero_counts >= 3
        filtered_df.loc[to_nan, replicate_cols] = np.nan

        median_abundance = filtered_df[replicate_cols].median(axis=1, skipna=True)
        median_condition = median_abundance.median(skipna=True)

        peptides_retained = filtered_df[replicate_cols].notna().any(axis=1).sum()
        percent_retained = (peptides_retained / total_peptides) * 100

        summary.append({
            'Condition': condition,
            'Median_Abundance': median_condition,
            'Percent_Peptides_Retained': percent_retained
        })

    summary_df = pd.DataFrame(summary)
    summary_df.to_csv(os.path.join(output_folder, f"{dataset_name}_TaskE.csv"), index=False)
    filtered_df.to_csv(os.path.join(output_folder, f"{dataset_name}_Filtered.csv"), index=False)
    print(f"Task E completed for {dataset_name} (handled separately).")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    print("Select P1, P2_scaled_by_mean, and P2_scaled_by_median CSV files...")
    file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])

    if file_paths and len(file_paths) == 3:
        print("Select output folder...")
        output_folder = filedialog.askdirectory()

        p1_file, p2_mean_file, p2_median_file = file_paths

        p1_df = pd.read_csv(p1_file)
        p2_mean_df = pd.read_csv(p2_mean_file)
        p2_median_df = pd.read_csv(p2_median_file)

        # Task A
        process_task_a(p1_df).to_csv(os.path.join(output_folder, "P1_TaskA.csv"), index=False)
        process_task_a(p2_mean_df).to_csv(os.path.join(output_folder, "P2_TaskA.csv"), index=False)
        print("Task A completed.")

        # Task B - Separate
        process_task_b([p1_df]).to_csv(os.path.join(output_folder, "P1_TaskB.csv"), index=False)
        process_task_b([p2_mean_df]).to_csv(os.path.join(output_folder, "P2_TaskB.csv"), index=False)
        print("Task B completed.")

        # Task C
        process_task_c(p1_df).to_csv(os.path.join(output_folder, "P1_TaskC.csv"), index=False)
        process_task_c(p2_median_df).to_csv(os.path.join(output_folder, "P2_TaskC.csv"), index=False)
        print("Task C completed.")

        # Task D - Separate
        process_task_d([p1_df]).to_csv(os.path.join(output_folder, "P1_TaskD.csv"), index=False)
        process_task_d([p2_median_df]).to_csv(os.path.join(output_folder, "P2_TaskD.csv"), index=False)
        print("Task D completed.")

        # Task E
        process_task_e_fixed(p1_df, "P1", output_folder)
        process_task_e_fixed(p2_mean_df, "P2", output_folder)

    else:
        print("Please select exactly three files (P1, P2_scaled_by_mean, P2_scaled_by_median). Exiting.")
