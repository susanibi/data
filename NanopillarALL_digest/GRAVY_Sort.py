#This script sorts the output from Calc_Gravy and removes a few columns

import pandas as pd
import os
import re
from tkinter import Tk, filedialog


def simplify_sample_name(path):
    filename = os.path.basename(path)
    name = filename.replace('.raw', '')
    match = re.search(r'(qc_\d+pg_\d+|\d+p\d+_\d+pg(?:_\w+)*_\d+)', name, re.IGNORECASE)
    if match:
        return match.group(1)
    # fallback to full filename without extension if pattern doesn't match
    return name


def process_gravy_sort():
    root = Tk()
    root.withdraw()

    # Ask user to choose an Excel file with multiple sheets
    file_path = filedialog.askopenfilename(
        title="Select Excel file with GRAVY data",
        filetypes=[("Excel Files", "*.xlsx *.xls")]
    )
    if not file_path:
        print("No file selected.")
        return

    # Read all sheets
    xls = pd.ExcelFile(file_path)
    new_sheets = {}

    for sheet_name in xls.sheet_names:
        try:
            df = xls.parse(sheet_name)

            required_cols = [
                "Stripped.Sequence",
                "GRAVY",
                "Protein.Group",
                "Precursor.Charge"
            ]

            # Identify sample columns
            sample_cols = [col for col in df.columns if col not in required_cols and not any(
                key in col for key in ["Protein", "Sequence", "Charge", "GRAVY"])]

            # Simplify sample column names
            rename_map = {col: simplify_sample_name(col) for col in sample_cols}
            df.rename(columns=rename_map, inplace=True)

            final_cols = required_cols + list(rename_map.values())
            df_filtered = df[final_cols].copy()

            # Sort by GRAVY ascending
            df_sorted = df_filtered.sort_values(by="GRAVY", ascending=True)

            # Add to output dictionary
            new_sheets[f"{sheet_name}_GRAVY_sorted"] = df_sorted

        except Exception as e:
            print(f"❌ Error processing sheet '{sheet_name}': {e}")

    if not new_sheets:
        print("No sheets processed.")
        return

    # Ask where to save
    save_path = filedialog.asksaveasfilename(
        title="Save sorted GRAVY Excel file",
        defaultextension=".xlsx",
        filetypes=[("Excel Files", "*.xlsx")]
    )

    if save_path:
        with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
            for sheet, data in new_sheets.items():
                data.to_excel(writer, sheet_name=sheet[:31], index=False)
        print(f"✅ File saved: {save_path}")
    else:
        print("No output file saved.")


if __name__ == "__main__":
    process_gravy_sort()
