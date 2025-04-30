import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from tkinter import Tk, filedialog

# Set up Tkinter file dialog
root = Tk()
root.withdraw()

# Select file
file_path = filedialog.askopenfilename(
    title="Select your replicate-level CSV file (Filtered_LongFormat.csv)",
    filetypes=[("CSV files", "*.csv")]
)

if not file_path:
    print("No file selected. Exiting.")
else:
    print(f"Selected file: {file_path}")

    # Load data
    df = pd.read_csv(file_path)

    # Preprocessing
    df['SurfaceType'] = df['Position'].apply(lambda pos: '3.2' if '3p2' in str(pos)
                                                        else '3.5' if '3p5' in str(pos)
                                                        else '5.5' if '5p5' in str(pos)
                                                        else 'Unknown')
    df['Log2Intensity'] = np.log2(df['Intensity'] + 1)

    # Keep only 50pg and 250pg and known Chips
    df = df[df['Amount'].isin(['50pg', '250pg']) & (df['SurfaceType'].isin(['3.2', '3.5', '5.5']))]

    # Function to calculate Cohen's d
    def cohens_d(x, y):
        nx = len(x)
        ny = len(y)
        pooled_std = np.sqrt(((nx - 1) * np.var(x, ddof=1) + (ny - 1) * np.var(y, ddof=1)) / (nx + ny - 2))
        return (np.mean(x) - np.mean(y)) / pooled_std

    # Run t-tests
    ttest_results = []

    for amount in ['50pg', '250pg']:
        for chip in ['3.2', '3.5', '5.5']:
            data_acn = df[(df['Amount'] == amount) & (df['SurfaceType'] == chip) & (df['Extraction'] == 'ACN')]['Log2Intensity']
            data_noacn = df[(df['Amount'] == amount) & (df['SurfaceType'] == chip) & (df['Extraction'] == 'NoACN')]['Log2Intensity']

            if len(data_acn) >= 3 and len(data_noacn) >= 3:
                stat, p_value = ttest_ind(data_acn, data_noacn, equal_var=False)  # Welch's t-test
                effect_size = cohens_d(data_acn, data_noacn)
                ttest_results.append({
                    'Load': amount,
                    'ChipID': chip,
                    'T-test p-value': round(p_value, 4),
                    'Significant Difference?': 'Yes' if p_value < 0.05 else 'No',
                    "Cohen's d (Effect Size)": round(effect_size, 2)
                })
            else:
                ttest_results.append({
                    'Load': amount,
                    'ChipID': chip,
                    'T-test p-value': 'NA (too few samples)',
                    'Significant Difference?': 'Undetermined',
                    "Cohen's d (Effect Size)": 'NA'
                })

    # Display t-test results
    ttest_df = pd.DataFrame(ttest_results)
    print("\nT-test Results (Welch's correction) with Effect Sizes:")
    print(ttest_df)
