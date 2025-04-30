#combining samples into gravyscore-bins - ACtivate the needed outdata; optios: stdec, mean, median

import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import re

import numpy as np
import pandas as pd


def main():
    root = Tk()
    root.withdraw()
    pr_file = askopenfilename(title="Select the processed file", filetypes=[("CSV files", "*.csv")])
    if not pr_file:
        print("No file selected. Exiting script.")
        exit()

    # Load as DataFrame
    fileData = pd.read_csv(pr_file, sep=",")
    if "GravyScore" not in fileData.columns:
        print("Invalid file: No column called GravyScore")
        exit()

    # Create bins
    global_min = fileData["GravyScore"].min()
    global_max = fileData["GravyScore"].max()
    num_bins = 50
    bins = np.linspace(global_min, global_max, num_bins + 1)

    # Add bin column to filesData
    fileData["GravyScore_bin"] = np.digitize(fileData["GravyScore"], bins, right=False)

    # Now use the bin_index to add bin_start and bin_end
    fileData["bin_start"] = fileData["GravyScore_bin"].apply(
        lambda i: bins[i - 1] if 0 < i <= len(bins) else np.nan
    )

    # Detect sample columns: those that contain a number in their name
    sample_columns = [col for col in fileData.columns if re.search(r'\d', col)]

    # Group and aggregate
    #binMethod = "mean"
    #binMethod = "std"
    binMethod = "median"
    # binMethod = "sum"
    agg_dict = {"GravyScore": "count"}  # Start with count (we'll rename this later)
    for col in sample_columns:
        agg_dict[col] = binMethod

    grouped = fileData.groupby("GravyScore_bin").agg(agg_dict).reset_index()

    # Rename count column
    grouped.rename(columns={"GravyScore": "peptides_count"}, inplace=True)

    # Ensure all bins are present (reindex)
    grouped = grouped.set_index("GravyScore_bin").reindex(range(1, num_bins + 1), fill_value=0).reset_index()

    # Add bin_start
    grouped["bin_start"] = grouped["GravyScore_bin"].apply(
        lambda i: bins[i - 1] if 0 < i <= len(bins) else np.nan
    )

    # Round values
    grouped["bin_start"] = grouped["bin_start"].round(2)
    grouped[sample_columns] = grouped[sample_columns].round(2)

    # Create a new DataFrame with just the relevant columns and sort by bin
    out = grouped[["bin_start", "peptides_count"] + sample_columns].sort_values("bin_start")

    # Print to file
    selected_dir = os.path.dirname(pr_file)
    processed_data_filename = os.path.splitext(os.path.basename(pr_file).rstrip('\r\n'))[0]
    output_file = os.path.join(selected_dir, 'binned ' + binMethod + ', ' + processed_data_filename +'.csv')

    out.to_csv(output_file, index=False)

    print("Result written to: \n" + output_file)
    return output_file


if __name__ == "__main__":
    main()
