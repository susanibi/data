import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog

def group_replicates(df, suffixes):
    grouped_df = pd.DataFrame()
    for suffix in suffixes:
        columns_to_group = [col for col in df.columns if col.endswith(suffix)]
        if columns_to_group:
            grouped_df[suffix] = df[columns_to_group].mean(axis=1)
    grouped_df.insert(0, 'GRAVY_bin', df['GRAVY_bin'])
    return grouped_df

def plot_mean_abundance(mean_abundance_df_grouped):
    plt.figure(figsize=(12, 6))
    for column in mean_abundance_df_grouped.columns[1:]:
        plt.plot(mean_abundance_df_grouped['GRAVY_bin'], mean_abundance_df_grouped[column], label=column)
    plt.title('Mean Abundance Per GRAVY Bin (Grouped)')
    plt.xlabel('GRAVY Bin')
    plt.ylabel('Mean Abundance')
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=5)
    plt.grid(True)
    plt.savefig('mean_abundance_per_gravy_bin_grouped.png')
    plt.show()

def main():
    root = Tk()
    root.withdraw()  # Hide the root window

    # Prompt user to select the Mean Abundance file
    mean_abundance_file = filedialog.askopenfilename(title="Select the Mean Abundance file", filetypes=[("Excel files", "*.xlsx")])
    mean_abundance_df = pd.read_excel(mean_abundance_file, engine='openpyxl')

    # Prompt user to select the PSM Per Gravy Per Sample file
    psm_per_gravy_file = filedialog.askopenfilename(title="Select the PSM Per Gravy Per Sample file", filetypes=[("Excel files", "*.xlsx")])
    psm_per_gravy_df = pd.read_excel(psm_per_gravy_file, engine='openpyxl')

    # Define suffixes for replicates
    suffixes = [f'_{i}' for i in range(1, 11)]

    # Group replicates in Mean Abundance Data
    mean_abundance_df_grouped = group_replicates(mean_abundance_df, suffixes)

    # Group replicates in PSM Per Gravy Per Sample Data
    psm_per_gravy_df_grouped = group_replicates(psm_per_gravy_df, suffixes)

    # Plot Mean Abundance Data (Grouped)
    plot_mean_abundance(mean_abundance_df_grouped)

if __name__ == "__main__":
    main()
