import tkinter as tk
from tkinter import filedialog
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def select_file():
    """Open file dialog to select the Excel file and process data."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    file_path = filedialog.askopenfilename(
        title="Select an Excel File",
        filetypes=[("Excel Files", "*.xlsx *.xls")]
    )

    if not file_path:
        print("No file selected. Exiting.")
        return

    print(f"Selected file: {file_path}")

    # Load the selected Excel file
    xls = pd.ExcelFile(file_path)

    # Check for a sheet that contains %PSM data
    sheet_name = "%PSM_individualEXP"  # Adjust if necessary
    if sheet_name not in xls.sheet_names:
        print(f"Sheet '{sheet_name}' not found. Available sheets: {xls.sheet_names}")
        return

    # Read the data
    df_psm = pd.read_excel(xls, sheet_name=sheet_name)

    # Ensure numeric values
    for column in df_psm.columns[1:]:  # Exclude GRAVY_Bin column
        df_psm[column] = pd.to_numeric(df_psm[column], errors='coerce')

    # Set GRAVY Bin as index for heatmap format
    df_heatmap = df_psm.set_index("GRAVY_Bin").T  # Transpose for heatmap format

    # ---- Generate Heatmap ----
    plt.figure(figsize=(12, 8))
    sns.heatmap(df_heatmap, cmap="YlGn", linewidths=0.5, annot=False)
    plt.xlabel("GRAVY Bin")
    plt.ylabel("Sample Conditions")
    plt.title("Heatmap of %PSM Across GRAVY Bins (Yellow-Green)")

    # Save the figure in the same directory as the input file
    output_folder = os.path.dirname(file_path)
    heatmap_file = os.path.join(output_folder, "heatmap_psm.png")
    plt.savefig(heatmap_file, dpi=300, bbox_inches="tight")

    print(f"Heatmap saved as: {heatmap_file}")

    # Show the heatmap
    plt.show()

    # ---- Generate Density Plot (KDE) ----
    plt.figure(figsize=(12, 6))
    for column in df_psm.columns[1:]:  # Exclude GRAVY_Bin column
        sns.kdeplot(df_psm[column], label=column, fill=True, alpha=0.5)

    plt.xlabel("%PSM")
    plt.ylabel("Density")
    plt.title("Density Distribution of %PSM Across Experimental Conditions")
    plt.legend(loc="upper right", bbox_to_anchor=(1.3, 1))
    plt.grid(True)

    # Save the density plot
    density_file = os.path.join(output_folder, "density_psm.png")
    plt.savefig(density_file, dpi=300, bbox_inches="tight")

    print(f"Density plot saved as: {density_file}")

    # Show the density plot
    plt.show()

if __name__ == "__main__":
    select_file()
