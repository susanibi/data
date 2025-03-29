import os
import re
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import openpyxl
import pandas as pd


def select_image_directory(title: str = "Select directory") -> str:
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open a dialog to select a folder
    folder_selected = filedialog.askdirectory(title=title)

    # Return the selected path
    return folder_selected

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


def save_file_dialog(droplets_count: int) -> str:
    # Initialize the Tkinter root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Generate a dynamic default filename based on the current date
    default_filename = f"droplet_analysis_{datetime.now().strftime('%Y%m%d')}.xlsx"

    # Open the "Save As" dialog
    file_path = filedialog.asksaveasfilename(
        title="Save " + str(droplets_count) + " results to Excel file",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile=default_filename
    )

    return file_path


def get_first_image_filepath(directory_path: str) -> str:
    for filename in os.listdir(directory_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            return directory_path + "/" + filename


def extract_info_from_filename(filename):
    # Regular expression to extract the date-time portion and the number after "ScanArea"
    match = re.search(r'Exp\d+__(\d{8})_ScanArea_(\d+)', filename)

    if match:
        # Extract the date string
        date_str = match.group(1)

        # Extract the number after "ScanArea"
        scan_area_number = match.group(2)

        # Convert the date string to YYYY-MM-DD format
        date_formatted = datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")

        # Since the time string is not present in the filename, we'll use a placeholder or skip it
        time_formatted = "00:00:00"  # Placeholder time

        # Combine date and time
        timestamp = f"{date_formatted} {time_formatted}"

        return scan_area_number, timestamp
    else:
        raise ValueError("Filename format does not match expected pattern")


def write_to_excel(droplets: list, output_excel_file: str) -> None:
    df = pd.DataFrame([vars(dto) for dto in droplets])
    df.to_excel(output_excel_file, index=False)
    print(f"Results saved to {output_excel_file}")
    add_hyperlinks_to_column(output_excel_file, "Sheet1", "A")


def add_hyperlinks_to_column(excel_file, sheet_name, column_letter):
    # Load the workbook and select the sheet
    wb = openpyxl.load_workbook(excel_file)
    sheet = wb[sheet_name]

    # Iterate over all rows in the specified column
    for row in range(1, sheet.max_row + 1):
        cell = f"{column_letter}{row}"
        file_path = sheet[cell].value

        if file_path:  # Ensure the cell is not empty
            sheet[cell].hyperlink = file_path
            sheet[cell].style = "Hyperlink"  # Style the cell as a hyperlink

    # Save the workbook
    wb.save(excel_file)
    print(f"Hyperlinks added to all cells in column {column_letter}.")


def open_excel_file(file_path):
    os.startfile(file_path)


