import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

# === User Settings ===
F_COLOR = '#2ca25f'      # Teal for F
R_COLOR = '#2b8cbe'      # Soft Blue for R
MEDIAN_LINE_COLOR = 'white'
FONT_SIZE_TITLE = 14
FONT_SIZE_LABELS = 12

def preprocess_data(df):
    data = []
    for col in df.columns:
        if col.startswith('F_') or col.startswith('R_'):
            roughness = int(col.split('_')[1].split('.')[0])
            material = 'F' if col.startswith('F_') else 'R'
            for value in df[col]:
                if value != 0:  # Ignore zeros
                    data.append({'Roughness': roughness, 'Median': value, 'Material': material})
    return pd.DataFrame(data)

def main():
    # === File Selection ===
    root = tk.Tk()
    root.withdraw()
    print("Select the first dataset (with F_1 to F_5, R_1 to R_5)...")
    file1 = filedialog.askopenfilename(title="Select First Violin Data CSV", filetypes=[("CSV Files", "*.csv")])
    print(f"Selected first file: {file1}\n")

    print("Select the second dataset (with F_6 to F_10, R_6 to R_10)...")
    file2 = filedialog.askopenfilename(title="Select Second Violin Data CSV", filetypes=[("CSV Files", "*.csv")])
    print(f"Selected second file: {file2}\n")

    # === Load Data ===
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Preprocess data
    df1_processed = preprocess_data(df1)
    df2_processed = preprocess_data(df2)
    df = pd.concat([df1_processed, df2_processed], ignore_index=True)

    # === Plot ===
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.violinplot(
        data=df,
        x='Roughness',
        y='Median',
        hue='Material',
        split=True,
        palette={'F': F_COLOR, 'R': R_COLOR},
        inner=None,
        linewidth=1.2,
        ax=ax
    )

    # Overlay custom median and quartile lines
    for roughness in df['Roughness'].unique():
        for material, color in zip(['F', 'R'], [F_COLOR, R_COLOR]):
            subset = df[(df['Roughness'] == roughness) & (df['Material'] == material)]
            if not subset.empty:
                median_val = subset['Median'].median()
                q1 = subset['Median'].quantile(0.25)
                q3 = subset['Median'].quantile(0.75)
                pos = roughness - 0.2 if material == 'F' else roughness + 0.2
                ax.hlines(median_val, pos - 0.1, pos + 0.1, color=MEDIAN_LINE_COLOR, linewidth=2)
                ax.hlines([q1, q3], pos - 0.05, pos + 0.05, color=MEDIAN_LINE_COLOR, linewidth=1, linestyles='dotted')

    # Formatting
    ax.set_title('Styled Violin Plot: Median & Quartiles', fontsize=FONT_SIZE_TITLE)
    ax.set_ylabel('Median Peptide Intensity (No Zeros)', fontsize=FONT_SIZE_LABELS)
    ax.set_xlabel('Surface Roughness Level', fontsize=FONT_SIZE_LABELS)
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    ax.legend(title='Material', title_fontsize=11, loc='lower right')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
