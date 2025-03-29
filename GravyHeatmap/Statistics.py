import pandas as pd
import scipy.stats as stats
import tkinter as tk
from tkinter import filedialog, messagebox
import re

def select_file():
    """Open file dialog to select the raw dataset."""
    root = tk.Tk()
    root.withdraw()  # Hide root window
    file_path = filedialog.askopenfilename(title="Select Merged Raw Data CSV",
                                           filetypes=[("CSV Files", "*.csv")])
    return file_path

def extract_condition(name):
    """
    Extracts the correct condition name from replicate labels.
    Handles Evo, Plate, R1_0.x, R2_0.x, F1_0.x, F2_0.x, and F_1.x, F_2.x, ..., F_10.x (same for R).
    """
    # Match patterns for different formats
    evo_match = re.match(r"Evo", name)
    plate_match = re.match(r"Plate", name)
    f1_match = re.match(r"F1_\d+\.\d", name)
    f2_match = re.match(r"F2_\d+\.\d", name)
    r1_match = re.match(r"R1_\d+\.\d", name)
    r2_match = re.match(r"R2_\d+\.\d", name)
    fx_match = re.match(r"F_\d+\.\d", name)  # Matches F_1.x to F_10.x
    rx_match = re.match(r"R_\d+\.\d", name)  # Matches R_1.x to R_10.x

    # Assign condition names properly
    if evo_match:
        return "Evo"
    elif plate_match:
        return "Plate"
    elif f1_match:
        return "F1"
    elif f2_match:
        return "F2"
    elif r1_match:
        return "R1"
    elif r2_match:
        return "R2"
    elif fx_match:
        return fx_match.group(0)  # Keep F_1, F_2, etc.
    elif rx_match:
        return rx_match.group(0)  # Keep R_1, R_2, etc.
    else:
        return name  # If no match, keep original (failsafe)

def analyze_data(file_path):
    """Loads the dataset, computes means, performs tests, and saves results."""
    try:
        # Load dataset
        df_raw = pd.read_csv(file_path)

        # Ensure the first column contains replicate labels and extract relevant data
        df_raw = df_raw.set_index(df_raw.columns[0])  # Set first column as index
        df_numeric = df_raw.astype(float)  # Convert all values to numeric

        # Group data correctly based on extracted condition names
        df_means = df_numeric.groupby(df_raw.index.map(extract_condition)).mean()

        # Identify "Evo" and other conditions
        if "Evo" in df_means.index:
            evo_values = df_means.loc["Evo"]
        else:
            messagebox.showerror("Error", "Evo not found in dataset. Please check your dataset.")
            return

        # Store test results
        test_results_list = []

        # Loop through all other conditions and compare with Evo
        for condition in df_means.index:
            if condition != "Evo":
                condition_values = df_means.loc[condition]

                # Kolmogorov-Smirnov Test
                ks_stat, ks_pvalue = stats.ks_2samp(evo_values, condition_values)

                # Mann-Whitney U Test
                mw_stat, mw_pvalue = stats.mannwhitneyu(evo_values, condition_values, alternative="two-sided")

                # Append results
                test_results_list.append({
                    "Comparison": f"Evo vs. {condition}",
                    "KS Statistic": ks_stat,
                    "KS p-value": ks_pvalue,
                    "MW Statistic": mw_stat,
                    "MW p-value": mw_pvalue,
                    "Conclusion": "Significant difference (p < 0.05)" if ks_pvalue < 0.05 or mw_pvalue < 0.05 else "No significant difference"
                })

        # Convert results to a DataFrame
        pairwise_test_results = pd.DataFrame(test_results_list)

        # Save results to a CSV file
        save_path = file_path.replace(".csv", "_Evo_vs_Conditions_Results.csv")
        pairwise_test_results.to_csv(save_path, index=False)

        # Display success message
        messagebox.showinfo("Success", f"Analysis complete!\nResults saved as:\n{save_path}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Run file selection and analysis
if __name__ == "__main__":
    file_path = select_file()
    if file_path:
        analyze_data(file_path)
