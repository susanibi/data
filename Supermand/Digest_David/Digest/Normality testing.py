import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
from scipy.stats import shapiro

# Set up Tkinter to select file
root = Tk()
root.withdraw()

# File dialog
file_path = filedialog.askopenfilename(
    title="Select your replicate-level CSV file (Filtered_LongFormat.csv)",
    filetypes=[("CSV files", "*.csv")]
)

# Confirm file selected
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

    # Focus only on 250pg and known Chips
    df = df[(df['Amount'] == '250pg') & (df['SurfaceType'].isin(['3.2', '3.5', '5.5']))]

    # Group and perform Shapiro-Wilk test
    results = []

    for chip in ['3.2', '3.5', '5.5']:
        for extraction in ['ACN', 'NoACN']:
            subset = df[(df['SurfaceType'] == chip) & (df['Extraction'] == extraction)]['Log2Intensity']

            if len(subset) >= 3:  # Shapiro requires at least 3 points
                stat, p_value = shapiro(subset)
                results.append({
                    'ChipID': chip,
                    'Extraction': extraction,
                    'Sample Size': len(subset),
                    'Shapiro-Wilk p-value': round(p_value, 4),
                    'Normal?': 'Yes' if p_value > 0.05 else 'No'
                })
            else:
                results.append({
                    'ChipID': chip,
                    'Extraction': extraction,
                    'Sample Size': len(subset),
                    'Shapiro-Wilk p-value': 'NA (too few samples)',
                    'Normal?': 'Undetermined'
                })

    # Display results
    results_df = pd.DataFrame(results)
    print("\nNormality Check Results (Shapiro-Wilk test):")
    print(results_df)
