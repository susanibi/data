import os
import re
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import askdirectory

# 📂 Select folder containing images
Tk().withdraw()
folder_path = askdirectory(title="Select the folder containing images")

if not folder_path:
    print("No folder selected. Exiting.")
    exit()

# Create a subfolder for ROI images
roi_folder = os.path.join(folder_path, "ROIs")
os.makedirs(roi_folder, exist_ok=True)

# Get all image files in the folder
image_files = sorted([f for f in os.listdir(folder_path) if f.endswith((".jpg", ".png", ".tif"))])

if not image_files:
    print("No image files found in the selected folder. Exiting.")
    exit()

# 🎯 Extract timestamp from filename
def extract_time_from_filename(filename):
    match = re.search(r"(\d{8})_ScanArea_(\d{6})", filename)
    if match:
        date_part, time_part = match.groups()
        return date_part, time_part
    return None, None


# 🎯 Detect & measure spots
def detect_large_spots(image_path, save_roi=True):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    _, binary = cv2.threshold(blurred, 65, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area, max_area = 2000, 50000
    large_spots = [cnt for cnt in contours if min_area < cv2.contourArea(cnt) < max_area]

    # Extract area, perimeter, and circularity
    spot_data = []
    for cnt in large_spots:
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)
        circularity = 4 * np.pi * (area / (perimeter ** 2)) if perimeter > 0 else 0
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            centroid_x, centroid_y = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
            spot_data.append((centroid_x, centroid_y, area, perimeter, circularity))

    spot_data.sort(key=lambda x: (x[1], x[0]))

    # Save image with contours
    if save_roi:
        image_with_contours = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(image_with_contours, large_spots, -1, (0, 255, 0), 2)
        cv2.imwrite(os.path.join(roi_folder, os.path.basename(image_path)), image_with_contours)

    return spot_data

# 🎯 Process images & extract time
image_data, detected_spots_data, elapsed_times = [], [], []
time_labels, elapsed_time_labels = [], []
first_timestamp = None

for filename in image_files:
    date_str, time_str = extract_time_from_filename(filename)
    if date_str and time_str:
        image_data.append((filename, date_str, time_str))

image_data.sort(key=lambda x: x[2])

for i, (filename, date_str, time_str) in enumerate(image_data):
    current_time = datetime.strptime(time_str, "%H%M%S")
    elapsed_time = 0 if i == 0 else (current_time - first_timestamp).total_seconds() / 60
    first_timestamp = first_timestamp or current_time
    elapsed_times.append(round(elapsed_time, 0))  # Rounded to full integers

    time_labels.append(time_str)
    elapsed_time_labels.append(elapsed_times[-1])

    spots = detect_large_spots(os.path.join(folder_path, filename), save_roi=True)
    detected_spots_data.append(spots)

# 🎯 Ensure all detected spots have the same number of entries
max_spots = max(len(spots) for spots in detected_spots_data)

# Function to pad missing spots with NaN
def pad_missing_spots(spot_list, max_length):
    return spot_list + [np.nan] * (max_length - len(spot_list))

# Pad all spot detections to ensure consistency
area_data = [pad_missing_spots([spot[2] for spot in spots], max_spots) for spots in detected_spots_data]
perimeter_data = [pad_missing_spots([spot[3] for spot in spots], max_spots) for spots in detected_spots_data]
circularity_data = [pad_missing_spots([spot[4] for spot in spots], max_spots) for spots in detected_spots_data]

# 🎯 Convert DataFrames into Correct Format (Fix Column Mismatch)
spot_labels = [f"Spot{i+1}" for i in range(max_spots)]

area_df = pd.DataFrame(area_data, index=time_labels, columns=spot_labels).T  # Transpose to fix shape mismatch
perimeter_df = pd.DataFrame(perimeter_data, index=time_labels, columns=spot_labels).T
circularity_df = pd.DataFrame(circularity_data, index=time_labels, columns=spot_labels).T

# Fix: Ensure elapsed_time_labels matches the number of rows
elapsed_time_series = pd.Series(elapsed_time_labels, index=time_labels)

# 🎯 Volume Calculation (Fix for Data Type Issue)
area_numeric = area_df.apply(pd.to_numeric, errors="coerce")  # Convert to numeric
# Updated volume estimation using V = V0 * (A / A0)^(3/2)
A0 = 4079.0  # Reference area in pixels² for 50 nL droplet
V0 = 50.0    # Reference volume in nanoliters

volume_data = ((area_numeric / A0) ** 1.5) * V0  # Area-only model


# Convert `volume_data` into a Pandas DataFrame with correct structure
volume_df = pd.DataFrame(volume_data, index=spot_labels, columns=time_labels).T  # Transposed for correct shape

# 🎯 Save to Excel with Proper Formatting
output_path = os.path.join(folder_path, "spot_analysis_results_fixed.xlsx")

with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
    elapsed_time_series.to_excel(writer, sheet_name="Metadata")
    area_df.to_excel(writer, sheet_name="Area")
    perimeter_df.to_excel(writer, sheet_name="Perimeter")
    circularity_df.to_excel(writer, sheet_name="Circularity")
    volume_df.to_excel(writer, sheet_name="Estimated Volume (nL)")

print(f"✅ Results saved to: {output_path}")

# 🎨 Plot Volume Over Time
plt.figure(figsize=(8, 5))
for spot in volume_df.columns:
    plt.plot(elapsed_time_labels, volume_df[spot], marker="o", label=spot)

plt.xlabel("Elapsed Time (minutes)")
plt.ylabel("Estimated Volume (nL)")
plt.title("Change in Droplet Volume Over Time")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.show()
