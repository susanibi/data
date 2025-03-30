import pandas as pd
import os
from tkinter import Tk, filedialog

def main():
    merge_files()


def merge_files():
    root = Tk()
    root.withdraw()
    pr_files = filedialog.askopenfilenames(title="Select files with processed tsv files")
    if not pr_files:
        return

    # Merge files into one table
    merged_data = {}
    for pr_file in pr_files:
        fileData = pd.read_csv(pr_file, sep=",")

        # Loop data and add to merged
        for _, row in fileData.iterrows():
            seq = row["GravySequence"]
            if seq not in merged_data:
                merged_data[seq] = {
                    "GravySequence": seq,
                    "GravyScore": row["GravyScore"],
                    "Precursor.Charge": row["Precursor.Charge"]
                }

            # Add sample columns
            for col in fileData.columns:
                if any(char.isdigit() for char in col):
                    merged_data[seq][col] = row[col]

    # Convert the merged dictionary to a DataFrame
    merged_table = pd.DataFrame(merged_data.values())

    # Optional: fill missing sample columns with 0.0 (if needed)
    merged_table = merged_table.fillna(0.0)

    # Print data to file
    selected_dir = os.path.dirname(pr_file)
    filenames = [os.path.splitext(os.path.basename(fp))[0] for fp in pr_files]
    output_file = os.path.join(selected_dir, "-".join(filenames) + ' - merged.csv')

    merged_table.to_csv(output_file, index=False)

    return output_file


if __name__ == "__main__":
    main()
