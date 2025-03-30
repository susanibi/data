from tkinter import Tk
from tkinter.filedialog import askopenfilename
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog
import os
from matplotlib.colors import SymLogNorm


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

    # Color range
    data_min, data_max = df_merged.min().min(), df_merged.max().max()
    if data_min == data_max:
        norm = None
    else:
        norm = SymLogNorm(linthresh=1000, vmin=data_min, vmax=data_max)
    custom_cmap = "magma"  # Try alternatives like "viridis" or "YlOrRd"

    data_min, data_max = df_merged.min().min(), df_merged.max().max()
    if data_min == data_max:
        norm = None
    else:
        norm = SymLogNorm(linthresh=1000, vmin=data_min, vmax=data_max)
    custom_cmap = "magma"  # Try alternatives like "viridis" or "YlOrRd"

    # -------------------------------
    # Plot the heatmap
    # -------------------------------
    plt.figure(figsize=(20, 10))
    sns.heatmap(
        df_merged,
        cmap=custom_cmap,
        norm=norm,
        linewidths=0.5,
        linecolor='gray'
    )
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("GravyScore Bins")
    plt.ylabel("Samples")
    plt.title("Heatmap with Global Binning and Custom Sorted Samples")

    # -------------------------------
    # Save the heatmap and merged CSV
    # -------------------------------
    save_path = save_file()
    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Heatmap saved to: {save_path}")
        merged_csv_path = os.path.join(os.path.dirname(save_path), "merged_heatmap_data.csv")
        df_merged.to_csv(merged_csv_path)
        print(f"Merged CSV saved to: {merged_csv_path}")

    plt.show()

def save_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        title="Save Heatmap As",
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("PDF File", "*.pdf")]
    )
    return file_path


if __name__ == "__main__":
    main()
