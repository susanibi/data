import csv
from tkinter.filedialog import askopenfilename
import pandas as pd
import numpy as np
import os
from tkinter import Tk
from Functions.GravyHelper import GravyHelper


def main():
    prepare_raw_gravy_file()


def prepare_raw_gravy_file():
    root = Tk()
    root.withdraw()
    pr_file = askopenfilename(title="Select the file", filetypes=[("TSV files", "*.tsv")])

    if not pr_file:
        print("No file selected. Exiting script.")
        exit()

    # Raw data
    df = pd.read_csv(pr_file, sep="\t")

    data = {}

    # Add column with replaced unimod code
    if 'Modified.Sequence' in df.columns:
        data['Modified.Sequence'] = df['Modified.Sequence']
        data["GravySequence"] = df["Modified.Sequence"].apply(GravyHelper.replace_modification)

    elif 'Stripped.Sequence' in df.columns:
        data['Stripped.Sequence'] = df['Stripped.Sequence']
        data["GravySequence"] = df["Stripped.Sequence"]
    else:
        print("No Modified.Sequence nor Stripped.Sequence column in file.")
        exit()

    # Add gravy score column and charge
    data["GravyScore"] = data["GravySequence"].apply(GravyHelper.calculate_gravy)
    data['Precursor.Charge'] = df['Precursor.Charge']

    # Add sample columns
    raw_cols = [col for col in df.columns if col.endswith(".raw")]
    sample_map = {col: extract_clean_sample_name(col) for col in raw_cols}
    sample_map = {k: v for k, v in sample_map.items() if v is not None}
    if not sample_map:
        print("No sample_map")
        exit()

    for key, value in df.items():
        if key.endswith('.raw') and key in sample_map:
            new_key = sample_map[key]
            data[new_key] = value.fillna(0)

    # Sort by gravy score
    sorter = sorted(range(len(data["GravyScore"])), key=lambda i: data["GravyScore"][i])
    for col, colvalues in data.items():
        data[col] = [colvalues[i] for i in sorter]

    # Print data to file
    selected_dir = os.path.dirname(pr_file)
    processed_data_filename = os.path.basename(pr_file).rstrip('\r\n')
    output_file = os.path.join(selected_dir, processed_data_filename + '_processed.csv')

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header row using the dictionary keys
        writer.writerow(data.keys())
        # Zip together the lists to create rows and write them
        for row in zip(*data.values()):
            writer.writerow(row)

    return output_file


def extract_clean_sample_name(col_path):
    # Load sampleNames only once
    if not hasattr(extract_clean_sample_name, "sampleNames"):
        sampleNames = {}
        sampleNamesMapFile = askopenfilename(
            title="Select the file defining sample names",
            filetypes=[("CSV files", "*.csv")]
        )
        with open(sampleNamesMapFile, "r") as file:
            for line in file:
                path, label = line.strip().split("\t")
                sampleNames[path] = label  # store in a dictionary
        extract_clean_sample_name.sampleNames = sampleNames

    # Now use the cached data
    sampleNames = extract_clean_sample_name.sampleNames

    return sampleNames.get(col_path, "UNKNOWN")


def bin_gravy_column(gravy_values, bin_size=0.05):
    min_bin = np.floor(min(gravy_values) * 20) / 20
    max_bin = np.ceil(max(gravy_values) * 20) / 20
    bins = np.arange(min_bin, max_bin + bin_size, bin_size)
    labels = [f"{round(bins[i], 3)} to {round(bins[i + 1], 3)}" for i in range(len(bins) - 1)]
    return bins, labels


if __name__ == "__main__":
    main()
