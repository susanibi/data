import pandas as pd
import numpy as np
import os
from tkinter import Tk, filedialog

def process_gravy_excel():
    # Hide main tkinter window
    root = Tk()
    root.withdraw()

    # Ask user to select the Excel file
    file_path = filedialog.askopenfilename(
        title="Select the Excel file",
        filetypes=[("Excel Files", "*.xlsx *.xls")]
    )
    if not file_path:
        print("No file selected.")
        return

    # Load all sheets
    xls = pd.ExcelFile(file_path)
    all_data = []
    for sheet in xls.sheet_names:
        df = xls.parse(sheet)

        # Try to find the correct GRAVY column
        if "GRAVY_with_mod" in df.columns:
            df = df.rename(columns={"Modified.Sequence": "Precursor", "GRAVY_with_mod": "GRAVY"})
        elif "GRAVY" in df.columns:
            df = df.rename(columns={"Modified.Sequence": "Precursor"})
            # column is already named "GRAVY"
        else:
            print(f"❌ No GRAVY column found in sheet: {sheet}")
            continue  # Skip this sheet

        # Collect abundance columns
        abundance_cols = [col for col in df.columns if col.endswith(".raw")]

        # Proceed only if required columns are present
        if "Precursor" in df.columns and "GRAVY" in df.columns:
            df = df[["Precursor", "GRAVY"] + abundance_cols]
            df["Condition"] = sheet
            all_data.append(df)
        else:
            print(f"⚠️ Missing 'Precursor' or 'GRAVY' in sheet: {sheet}, skipping.")

    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df["GRAVY_bin"] = np.floor(combined_df["GRAVY"] * 10) / 10

    # Melt to long format
    melted_df = combined_df.melt(
        id_vars=["Precursor", "GRAVY_bin", "Condition"],
        value_vars=[col for col in combined_df.columns if col.endswith(".raw")],
        var_name="Replicate",
        value_name="Abundance"
    ).dropna()

    # Group by GRAVY_bin and Condition
    sum_df = (
        melted_df.groupby(["GRAVY_bin", "Condition"])["Abundance"]
        .sum()
        .reset_index()
        .pivot(index="GRAVY_bin", columns="Condition", values="Abundance")
        .sort_index()
    )

    mean_df = (
        melted_df.groupby(["GRAVY_bin", "Condition"])["Abundance"]
        .mean()
        .reset_index()
        .pivot(index="GRAVY_bin", columns="Condition", values="Abundance")
        .sort_index()
    )

    # Format numbers with comma decimals safely
    def format_comma(val):
        if isinstance(val, (int, float)):
            return f"{val:.4f}".replace('.', ',')
        return ""

    for col in sum_df.columns:
        sum_df[col] = sum_df[col].map(format_comma)

    for col in mean_df.columns:
        mean_df[col] = mean_df[col].map(format_comma)

    # Ask user where to save
    save_folder = filedialog.askdirectory(title="Select folder to save the Excel file")
    if not save_folder:
        print("No folder selected.")
        return

    output_path = os.path.join(save_folder, "gravy_binned_abundances.xlsx")

    # Write to Excel with two sheets
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        if not sum_df.empty:
            sum_df.to_excel(writer, sheet_name="Sum")
        if not mean_df.empty:
            mean_df.to_excel(writer, sheet_name="Mean")

    print(f"\n✅ File saved with two sheets (Sum, Mean):")
    print(f"   • {output_path}")

# Run it
if __name__ == "__main__":
    process_gravy_excel()
