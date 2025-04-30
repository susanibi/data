#create a mean over replicates to get sample level for each peptide.

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

    # Detect sample columns: those that contain a number in their name
    sample_cols = [col for col in fileData.columns if re.search(r'\d', col)]

    # Group these columns by sample name (excluding the replica index)
    sample_groups = {}
    for col in sample_cols:
        sample_name = col.rsplit(".", 1)[0]  # e.g., R_1.1 → R_1
        sample_groups.setdefault(sample_name, []).append(col)

    # Average across replicas
    for sample_name, replicas in sample_groups.items():
        fileData[sample_name] = fileData[replicas].mean(axis=1).round(2)

    # Drop the individual replica columns
    fileData.drop(columns=sample_cols, inplace=True)

    # This is where I need the logic that takes the average of all the replicas:
    out = fileData

    # Print to file
    selected_dir = os.path.dirname(pr_file)
    processed_data_filename = os.path.splitext(os.path.basename(pr_file).rstrip('\r\n'))[0]
    output_file = os.path.join(selected_dir, 'avg-replicas-' + processed_data_filename +'.csv')

    out.to_csv(output_file, index=False)

    print("Result written to: \n" + output_file)
    return output_file


if __name__ == "__main__":
    main()
