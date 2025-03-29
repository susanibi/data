import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os


# Function to open a file dialog and select a file
def select_file():
    # Initialize the Tkinter root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open the file dialog
    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")]
    )

    return file_path


# Function to read the file
def read_file(file_path):
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path, engine='openpyxl')
    else:
        df = pd.read_csv(file_path)
    return df


# Function to determine the groupings based on the headers
def determine_groups(df):
    if 'F_10.1' in df.columns:
        groups = {
            'F_10': ['F_10.1', 'F_10.2', 'F_10.3', 'F_10.4', 'F_10.5'],
            'R_10': ['R_10.1', 'R_10.2', 'R_10.3', 'R_10.4', 'R_10.5'],
            'F_9': ['F_9.1', 'F_9.2', 'F_9.3', 'F_9.4', 'F_9.5'],
            'R_9': ['R_9.1', 'R_9.2', 'R_9.3', 'R_9.4', 'R_9.5'],
            'F_8': ['F_8.1', 'F_8.2', 'F_8.3', 'F_8.4', 'F_8.5'],
            'R_8': ['R_8.1', 'R_8.2', 'R_8.3', 'R_8.4', 'R_8.5'],
            'F_7': ['F_7.1', 'F_7.2', 'F_7.3', 'F_7.4', 'F_7.5'],
            'R_7': ['R_7.1', 'R_7.2', 'R_7.3', 'R_7.4', 'R_7.5'],
            'F_6': ['F_6.1', 'F_6.2', 'F_6.3', 'F_6.4', 'F_6.5'],
            'R_6': ['R_6.1', 'R_6.2', 'R_6.3', 'R_6.4', 'R_6.5'],
            'Evo': ['Evo_1.1', 'Evo_1.2', 'Evo_1.3', 'Evo_1.4', 'Evo_1.5'],
            'Plate': ['Plate_1.1', 'Plate_1.2', 'Plate_1.3']
        }
    else:
        groups = {
            'R_1': ['R_1.1', 'R_1.2', 'R_1.3', 'R_1.4', 'R_1.5'],
            'F_1': ['F_1.1', 'F_1.2', 'F_1.3', 'F_1.4', 'F_1.5'],
            'R_2': ['R_2.1', 'R_2.2', 'R_2.3', 'R_2.4', 'R_2.5'],
            'F_2': ['F_2.1', 'F_2.2', 'F_2.3', 'F_2.4', 'F_2.5'],
            'R_3': ['R_3.1', 'R_3.2', 'R_3.3', 'R_3.4', 'R_3.5'],
            'F_3': ['F_3.1', 'F_3.2', 'F_3.3', 'F_3.4', 'F_3.5'],
            'R_4': ['R_4.1', 'R_4.2', 'R_4.3', 'R_4.4', 'R_4.5'],
            'F_4': ['F_4.1', 'F_4.2', 'F_4.3', 'F_4.4', 'F_4.5'],
            'R_5': ['R_5.1', 'R_5.2', 'R_5.3', 'R_5.4', 'R_5.5'],
            'F_5': ['F_5.1', 'F_5.2', 'F_5.3', 'F_5.4', 'F_5.5'],
            'F2': ['F2_0.1', 'F2_0.2', 'F2_0.3', 'F2_0.4', 'F2_0.5'],
            'R2': ['R2_0.1', 'R2_0.2', 'R2_0.3', 'R2_0.4', 'R2_0.5'],
            'R1': ['R1_0.1', 'R1_0.2', 'R1_0.3', 'R1_0.4', 'R1_0.5'],
            'F1': ['F1_0.1', 'F1_0.2', 'F1_0.3', 'F1_0.4', 'F1_0.5']
        }
    return groups


# Function to calculate statistics for each group
def calculate_statistics(df, groups):
    stats_data = {'GravyScores': df['GravyScores']}
    median_data = {'GravyScores': df['GravyScores']}
    mean_data = {'GravyScores': df['GravyScores']}
    mean_stdev_data = {'GravyScores': df['GravyScores']}
    min_max_data = {'GravyScores': df['GravyScores']}
    sum_data = {'GravyScores': df['GravyScores']}

    for group, cols in groups.items():
        data = df[cols].fillna(0)
        stats_data[f'{group}_median'] = data.median(axis=1)
        stats_data[f'{group}_Q1'] = data.quantile(0.25, axis=1)
        stats_data[f'{group}_Q3'] = data.quantile(0.75, axis=1)
        stats_data[f'{group}_min'] = data.min(axis=1)
        stats_data[f'{group}_max'] = data.max(axis=1)

        median_data[f'{group}_median'] = data.median(axis=1)

        mean_data[f'{group}_mean'] = data.mean(axis=1)
        mean_stdev_data[f'{group}_mean'] = data.mean(axis=1)
        mean_stdev_data[f'{group}_stdev'] = data.std(axis=1)

        min_max_data[f'{group}_min'] = data.min(axis=1)
        min_max_data[f'{group}_max'] = data.max(axis=1)

        sum_data[f'{group}_sum'] = data.sum(axis=1)

    return pd.DataFrame(stats_data), pd.DataFrame(median_data), pd.DataFrame(mean_data), pd.DataFrame(
        mean_stdev_data), pd.DataFrame(min_max_data), pd.DataFrame(sum_data)

# Function to save the restructured data to a new file using a save file dialog
def save_file_dialog(file_path: str) -> str:
    # Initialize the Tkinter root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Generate a new filename based on the original file name
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    new_filename = f"{base_name}_restructured.xlsx"

    # Open the "Save As" dialog
    file_path = filedialog.asksaveasfilename(
        title="Save results to Excel file",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile=new_filename
    )

    return file_path


# Function to save the restructured data to the chosen file path
def save_restructured_data(stats_data, median_data, mean_data, mean_stdev_data, min_max_data, sum_data, file_path):
    with pd.ExcelWriter(file_path) as writer:
        stats_data.to_excel(writer, sheet_name='Stats', index=False)
        median_data.to_excel(writer, sheet_name='Median', index=False)
        mean_data.to_excel(writer, sheet_name='Mean', index=False)
        mean_stdev_data.to_excel(writer, sheet_name='Mean_Stdev', index=False)
        min_max_data.to_excel(writer, sheet_name='Min_Max', index=False)
        sum_data.to_excel(writer, sheet_name='Sum', index=False)

    print(f"Restructured data saved to {file_path}")



# Main script execution
file_path = select_file()  # Open file dialog to select a file

if file_path:  # Check if a file was selected
    df = read_file(file_path)

    # Determine groups based on headers
    groups = determine_groups(df)

    # Calculate statistics for each group
    stats_data, median_data, mean_data, mean_stdev_data, min_max_data, sum_data = calculate_statistics(df, groups)

    output_file = save_file_dialog(file_path)
    if output_file:  # Check if a file path was provided for saving
        save_restructured_data(stats_data, median_data, mean_data, mean_stdev_data, min_max_data, sum_data, output_file)
else:
    print("No file selected.")