import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import matplotlib.cm as cm
import matplotlib.colors as mcolors

# Define gradient colors for Peptides (Warm Clay → Soft Taupe) and Proteins (Muted Copper)
peptide_gradient_cmap = mcolors.LinearSegmentedColormap.from_list(
    "peptide_gradient", ["#D8BFAA", "#897D75"]  # Warm Clay → Soft Taupe
)
protein_gradient_cmap = mcolors.LinearSegmentedColormap.from_list(
    "protein_gradient", ["#CA6768", "#914949"]  # Muted Copper Brown → Warm Sandstone
)

# Function to extract and analyze data
def extract_and_analyze(file_path):
    try:
        # Load the Excel file
        xls = pd.ExcelFile(file_path)

        # Ensure required sheets exist
        required_sheets = ["1HEKcell_dil_ACN", "1HEKcell_dil_NoACN_NoCTRLs"]
        for sheet in required_sheets:
            if sheet not in xls.sheet_names:
                raise ValueError(f"Error: Required sheet '{sheet}' not found in {file_path}")

        # Load relevant sheets
        df_acn = pd.read_excel(xls, sheet_name="1HEKcell_dil_ACN")
        df_noacn = pd.read_excel(xls, sheet_name="1HEKcell_dil_NoACN_NoCTRLs")

        # Check if dataframes are empty
        if df_acn.empty or df_noacn.empty:
            raise ValueError("Error: One or both data sheets are empty!")

        # Extract peptide and protein count columns
        peptide_col = "Peptide Count"
        protein_col = "Protein Count"

        if peptide_col not in df_acn.columns or peptide_col not in df_noacn.columns:
            raise ValueError(f"Error: Required column '{peptide_col}' not found in the sheets.")

        if protein_col not in df_acn.columns or protein_col not in df_noacn.columns:
            raise ValueError(f"Error: Required column '{protein_col}' not found in the sheets.")

        # Extract peptide and protein data
        acn_peptides = df_acn[peptide_col].dropna()
        noacn_peptides = df_noacn[peptide_col].dropna()

        acn_proteins = df_acn[protein_col].dropna()
        noacn_proteins = df_noacn[protein_col].dropna()

        # Perform independent t-tests
        peptide_ttest = ttest_ind(acn_peptides, noacn_peptides, nan_policy='omit', equal_var=False)
        protein_ttest = ttest_ind(acn_proteins, noacn_proteins, nan_policy='omit', equal_var=False)

        # Define font sizes
        fontsize = 12  # Base font size
        title_fontsize = fontsize + 1  # Larger for titles
        small_fontsize = fontsize - 4  # Smaller font for stats text

        # Create a statistical results dataframe
        statistical_results = pd.DataFrame({
            "Comparison": ["Peptides (ACN vs. No ACN)", "Proteins (ACN vs. No ACN)"],
            "t-Statistic": [peptide_ttest.statistic, protein_ttest.statistic],
            "p-Value": [peptide_ttest.pvalue, protein_ttest.pvalue]
        })

        # Create figure and axes with improved spacing
        fig = plt.figure(figsize=(15, 8), dpi=300)

        # Create custom axes positions for better control
        # [left, bottom, width, height]
        ax1 = fig.add_axes([0.12, 0.15, 0.35, 0.7])  # Left plot
        ax2 = fig.add_axes([0.58, 0.15, 0.35, 0.7])  # Right plot
        axes = [ax1, ax2]

        # Peptide Counts Boxplot (Gradient)
        df_melted_peptides = pd.DataFrame({
            "Condition": ["ACN"] * len(acn_peptides) + ["No ACN"] * len(noacn_peptides),
            "Peptide Count": pd.concat([acn_peptides, noacn_peptides])
        })

        # Generate gradient colors for Peptides
        peptide_gradient_colors = [peptide_gradient_cmap(0.2), peptide_gradient_cmap(0.8)]

        sns.boxplot(x="Condition", y="Peptide Count", data=df_melted_peptides,
                    ax=axes[0], palette=peptide_gradient_colors)

        # Add title and labels with specified font sizes
        axes[0].set_title("Peptide Count Distribution", fontsize=title_fontsize, pad=5)
        axes[0].set_xlabel("")  # Removes "Condition" label from x-axis
        axes[0].set_ylabel("Peptide Count", fontsize=fontsize)
        axes[0].set_xticklabels(["ACN", "No ACN"], fontsize=fontsize)

        # Add t-test results to the first plot
        pval_peptides = statistical_results["p-Value"][0]
        t_stat_peptides = statistical_results["t-Statistic"][0]
        stars = '***' if pval_peptides < 0.001 else '**' if pval_peptides < 0.01 else '*' if pval_peptides < 0.05 else 'ns'

        y_pos = df_melted_peptides["Peptide Count"].max() + (df_melted_peptides["Peptide Count"].max() * 0.05)
        axes[0].annotate(f"{stars}\nt={t_stat_peptides:.2f}, p={pval_peptides:.2e}",
                         xy=(0.5, y_pos),
                         xycoords=('axes fraction', 'data'),
                         ha='center',
                         fontsize=small_fontsize,
                         bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7))

        # Protein Counts Boxplot (Gradient)
        df_melted_proteins = pd.DataFrame({
            "Condition": ["ACN"] * len(acn_proteins) + ["No ACN"] * len(noacn_proteins),
            "Protein Count": pd.concat([acn_proteins, noacn_proteins])
        })

        # Generate gradient colors for Proteins
        protein_gradient_colors = [protein_gradient_cmap(0.2), protein_gradient_cmap(0.8)]

        sns.boxplot(x="Condition", y="Protein Count", data=df_melted_proteins,
                    ax=axes[1], palette=protein_gradient_colors)

        # Add title and labels with specified font sizes
        axes[1].set_title("Protein Count Distribution", fontsize=title_fontsize, pad=5)
        axes[1].set_xlabel("")  # Removes "Condition" label from x-axis
        axes[1].set_ylabel("Protein Count", fontsize=fontsize)
        axes[1].set_xticklabels(["ACN", "No ACN"], fontsize=fontsize)

        # Add t-test results to the second plot
        pval_proteins = statistical_results["p-Value"][1]
        t_stat_proteins = statistical_results["t-Statistic"][1]
        stars = '***' if pval_proteins < 0.001 else '**' if pval_proteins < 0.01 else '*' if pval_proteins < 0.05 else 'ns'

        y_pos = df_melted_proteins["Protein Count"].max() + (df_melted_proteins["Protein Count"].max() * 0.05)
        axes[1].annotate(f"{stars}\nt={t_stat_proteins:.2f}, p={pval_proteins:.2e}",
                         xy=(0.5, y_pos),
                         xycoords=('axes fraction', 'data'),
                         ha='center',
                         fontsize=small_fontsize,
                         bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7))

        # Set the Same Y-Axis Limits for Both Plots
        y_min = min(df_melted_peptides["Peptide Count"].min() - 200, df_melted_proteins["Protein Count"].min() - 200)
        y_max = max(df_melted_peptides["Peptide Count"].max() + 400, df_melted_proteins["Protein Count"].max() + 400)

        axes[0].set_ylim(y_min, y_max)
        axes[1].set_ylim(y_min, y_max)

        # Set tick font sizes
        for ax in axes:
            ax.tick_params(axis='both', which='major', labelsize=fontsize - 2)
            # Add grid lines for better readability
            ax.grid(True, axis='y', linestyle='--', alpha=0.5)
            ax.set_axisbelow(True)

        # Add an overall title to the figure
        fig.text(0.5, 0.95, "Comparison of ACN and No ACN Conditions",
                 ha='center', fontsize=title_fontsize + 2, weight='bold')

        # Save the figure
        plt.savefig("peptide_protein_boxplots.png", bbox_inches='tight', dpi=300)
        plt.show()
        # # Create a statistical results dataframe
        # statistical_results = pd.DataFrame({
        #     "Comparison": ["Peptides (ACN vs. No ACN)", "Proteins (ACN vs. No ACN)"],
        #     "t-Statistic": [peptide_ttest.statistic, protein_ttest.statistic],
        #     "p-Value": [peptide_ttest.pvalue, protein_ttest.pvalue]
        # })
        #
        # # 🎨 Visualization: Box Plot
        # fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        #
        # # Peptide Counts Boxplot (Gradient)
        # df_melted_peptides = pd.DataFrame({
        #     "Condition": ["ACN"] * len(acn_peptides) + ["No ACN"] * len(noacn_peptides),
        #     "Peptide Count": pd.concat([acn_peptides, noacn_peptides])
        # })
        #
        # # Generate gradient colors for Peptides
        # peptide_gradient_colors = [peptide_gradient_cmap(0.2), peptide_gradient_cmap(0.8)]
        #
        # sns.boxplot(x="Condition", y="Peptide Count", data=df_melted_peptides,
        #             ax=axes[0], palette=peptide_gradient_colors)
        #
        # axes[0].set_title("Peptide Count Distribution")
        # axes[0].set_xlabel("")  # Removes "Condition" label from x-axis
        # axes[0].set_xticklabels(["ACN", "No ACN"])  # Sets correct x-axis labels
        #
        # # Protein Counts Boxplot (Gradient)
        # df_melted_proteins = pd.DataFrame({
        #     "Condition": ["ACN"] * len(acn_proteins) + ["No ACN"] * len(noacn_proteins),
        #     "Protein Count": pd.concat([acn_proteins, noacn_proteins])
        # })
        #
        # # Generate gradient colors for Proteins
        # protein_gradient_colors = [protein_gradient_cmap(0.2), protein_gradient_cmap(0.8)]
        #
        # sns.boxplot(x="Condition", y="Protein Count", data=df_melted_proteins,
        #             ax=axes[1], palette=protein_gradient_colors)
        #
        # axes[1].set_title("Protein Count Distribution")
        # axes[1].set_xlabel("")  # Removes "Condition" label from x-axis
        # axes[1].set_xticklabels(["ACN", "No ACN"])  # Sets correct x-axis labels
        #
        # # ✅ Set the Same Y-Axis Limits for Both Plots
        # y_min = min(df_melted_peptides["Peptide Count"].min()-200, df_melted_proteins["Protein Count"].min())
        # y_max = max(df_melted_peptides["Peptide Count"].max()+200, df_melted_proteins["Protein Count"].max())
        #
        # axes[0].set_ylim(y_min, y_max)
        # axes[1].set_ylim(y_min, y_max)
        #
        # plt.tight_layout()
        # plt.show()

        # Return statistical results
        return statistical_results

    except Exception as e:
        print(f"Error encountered: {e}")
        return None

# Main function to prompt the user and run analysis
def main():
    # Ask the user to select an Excel file
    Tk().withdraw()
    file_path = askopenfilename(title="Select the Excel file", filetypes=[("Excel files", "*.xlsx")])

    if not file_path:
        print("No file selected. Exiting.")
        return

    # Perform analysis
    results = extract_and_analyze(file_path)

    if results is not None:
        print("\n--- Statistical Summary ---")
        print(results.to_string(index=False))

# Run the script
if __name__ == "__main__":
    main()
