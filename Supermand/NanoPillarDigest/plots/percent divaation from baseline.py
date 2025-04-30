import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tkinter import Tk, filedialog

# ==== SETTINGS ====
FONT_SIZE = 12        # Base font size
FIG_SIZE = (14, 6)    # Figure size

def median_ignore_zeros(series):
    non_zero_values = series[series != 0]
    if not non_zero_values.empty:
        return non_zero_values.median()
    else:
        return float('nan')

def collapse_replicates(df, prefix, start, end):
    collapsed = {}
    for i in range(start, end + 1):
        cols = [col for col in df.columns if col.startswith(f"{prefix}_{i}.")]
        if cols:
            collapsed[f"{prefix}_{i}"] = df[cols].apply(median_ignore_zeros, axis=1).median()
    return collapsed

def main():
    # File selection
    root = Tk()
    root.withdraw()
    print("Select the first dataset (with F_1 to F_5, R_1 to R_5)...")
    file1 = filedialog.askopenfilename()
    print(f"Selected first file: {file1}\n")

    print("Select the second dataset (with F_6 to F_10, R_6 to R_10)...")
    file2 = filedialog.askopenfilename()
    print(f"Selected second file: {file2}\n")

    # Load datasets
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Process first dataset
    f_first = collapse_replicates(df1, 'F', 1, 4)
    r_first = collapse_replicates(df1, 'R', 1, 4)
    f5_baseline = df1[[col for col in df1.columns if col.startswith('F_5.')]].apply(median_ignore_zeros, axis=1).median()
    r5_baseline = df1[[col for col in df1.columns if col.startswith('R_5.')]].apply(median_ignore_zeros, axis=1).median()
    f_first_pct = {k: ((v - f5_baseline) / f5_baseline) * 100 for k, v in f_first.items()}
    r_first_pct = {k: ((v - r5_baseline) / r5_baseline) * 100 for k, v in r_first.items()}

    # Process second dataset
    f_second = collapse_replicates(df2, 'F', 6, 10)
    r_second = collapse_replicates(df2, 'R', 6, 10)
    f6_baseline = df2[[col for col in df2.columns if col.startswith('F_6.')]].apply(median_ignore_zeros, axis=1).median()
    r6_baseline = df2[[col for col in df2.columns if col.startswith('R_6.')]].apply(median_ignore_zeros, axis=1).median()
    f_second_pct = {k: ((v - f6_baseline) / f6_baseline) * 100 for k, v in f_second.items()}
    r_second_pct = {k: ((v - r6_baseline) / r6_baseline) * 100 for k, v in r_second.items()}

    # Combine all
    all_data = {**f_first_pct, **r_first_pct, **f_second_pct, **r_second_pct}
    combined_df = pd.DataFrame(list(all_data.items()), columns=['Condition', 'Percent Deviation'])

    # Interleave F and R per number
    plot_data = []
    for i in range(1, 11):
        f_label = f'F_{i}'
        r_label = f'R_{i}'
        if f_label in combined_df['Condition'].values:
            plot_data.append(combined_df[combined_df['Condition'] == f_label].iloc[0])
        if r_label in combined_df['Condition'].values:
            plot_data.append(combined_df[combined_df['Condition'] == r_label].iloc[0])
    plot_df = pd.DataFrame(plot_data)

    # Create color gradients
    f_colors = plt.cm.BuGn(np.linspace(0.3, 1, 10))
    r_colors = plt.cm.Blues(np.linspace(0.3, 1, 10))

    # Assign colors based on gradient
    plot_df['Color'] = plot_df['Condition'].apply(lambda x: f_colors[int(x.split('_')[1]) - 1] if x.startswith('F_') else r_colors[int(x.split('_')[1]) - 1])

    # X-axis labels as 1-10, repeated for F/R
    x_labels = []
    for i in range(1, 11):
        if f'F_{i}' in plot_df['Condition'].values or f'R_{i}' in plot_df['Condition'].values:
            x_labels.append(str(i))

    # Plot
    plt.figure(figsize=FIG_SIZE)
    bar_width = 0.4
    indices = range(len(x_labels))
    f_bars = plt.bar([i - bar_width/2 for i in indices], plot_df[plot_df['Condition'].str.startswith('F_')]['Percent Deviation'], bar_width, color=plot_df[plot_df['Condition'].str.startswith('F_')]['Color'], label='F')
    r_bars = plt.bar([i + bar_width/2 for i in indices], plot_df[plot_df['Condition'].str.startswith('R_')]['Percent Deviation'], bar_width, color=plot_df[plot_df['Condition'].str.startswith('R_')]['Color'], label='R')
    plt.axhline(0, color='black', linewidth=0.8)
    plt.title('Percentage Deviation from Baseline (F & R Paired Conditions)', fontsize=FONT_SIZE + 2)
    plt.ylabel('Percent Deviation (%)', fontsize=FONT_SIZE)
    plt.xticks(ticks=indices, labels=x_labels, rotation=0, fontsize=FONT_SIZE)
    plt.tight_layout()
    plt.legend(['Baseline', 'F (BuGn)', 'R (Blues)'], loc='upper right', fontsize=FONT_SIZE)
    plt.show()

if __name__ == "__main__":
    main()
