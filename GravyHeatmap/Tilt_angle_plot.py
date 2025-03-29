import numpy as np
import matplotlib.pyplot as plt

# Corrected Input Data (Tilt Angles in Degrees)
data = {
    "H2O": {"TA_pillar": [57.0, 36.0, 32.0], "TA_smooth": [90.0, 90.0]},
    "TEAB": {"TA_pillar": [42.0, 52.0, 47.0, 46.0], "TA_smooth": [74.0]},
    "50pg": {"TA_pillar": [43.0, 90.0], "TA_smooth": [90.0]},
    "200pg": {"TA_pillar": [77.0, 90.0, 74.0], "TA_smooth": [74.0]},
}

# Define Custom Colors
custom_colors = {
    "H2O": "skyblue",
    "TEAB": "#468B97",
    "50pg": "#E6A8D7",
    "200pg": "#F4C2C2",
}

# Convert Tilt Angles from Degrees to Radians & Compute Mean & Standard Deviation
means_radians = {}
std_radians = {}

for reagent, angles in data.items():
    means_radians[reagent] = {
        key: np.radians(np.mean(vals)) for key, vals in angles.items()
    }
    std_radians[reagent] = {
        key: np.radians(np.std(vals, ddof=1)) if len(vals) > 1 else 0 for key, vals in angles.items()
    }

# Create Polar Plot
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))

# Lists to store legend items separately for sorting
pillar_handles = []
pillar_labels = []
smooth_handles = []
smooth_labels = []

for reagent, angles in means_radians.items():
    angle_pillar = angles["TA_pillar"]
    angle_smooth = angles.get("TA_smooth")  # Get TA_smooth if it exists

    # Standard deviation (error) in radians
    error_pillar = std_radians[reagent]["TA_pillar"]

    # Get reagent-specific color
    color = custom_colors.get(reagent, "black")

    # Compute mean angle in degrees
    mean_angle_pillar = np.degrees(angle_pillar)
    mean_angle_smooth = np.degrees(angle_smooth) if angle_smooth is not None else None

    # Plot Main Tilt Angle Line for `TA_pillar`
    line1, = ax.plot([angle_pillar, angle_pillar], [0, 1], linestyle='-', linewidth=2, color=color)

    # Add `TA_pillar` line to the sorted legend list
    pillar_handles.append(line1)
    pillar_labels.append(f"{reagent} - TA_pillar ({mean_angle_pillar:.1f}°)")

    # Plot `TA_smooth` as a Dot Instead of a Line
    if angle_smooth is not None:
        dot = ax.scatter(angle_smooth, 1, color=color, s=80, edgecolors="black", zorder=3)
        smooth_handles.append(dot)
        smooth_labels.append(f"{reagent} - TA_smooth ({mean_angle_smooth:.1f}°)")

    # Plot Shaded Standard Deviation for `TA_pillar`
    if error_pillar > 0:
        ax.fill_betweenx([0, 1], angle_pillar - error_pillar, angle_pillar + error_pillar,
                         alpha=0.2, color=color)

# Adjust Polar Plot Settings
ax.set_theta_zero_location("E")
ax.set_theta_direction(1)

# Set Tick Positions Before Labeling
tick_positions = [0, np.pi / 2, np.pi, 3 * np.pi / 2]
ax.set_xticks(tick_positions)
ax.set_xticklabels(["0° (East)", "90° (North)", "180° (West)", "270° (South)"])

# Remove Radial Labels (Numbers on Rings)
ax.set_yticklabels([])

# Move Title Higher to Avoid Overlap
ax.set_title("Tilt Angle Comparison (Polar Plot) - Shaded Std Dev", y=1.15)

# Combine Sorted Legend Items (TA_pillar first, then TA_smooth)
ax.legend(pillar_handles + smooth_handles, pillar_labels + smooth_labels, loc="upper right", bbox_to_anchor=(1.3, 1))

# Display Plot
plt.show()
import numpy as np
import matplotlib.pyplot as plt

# Corrected Input Data (Tilt Angles in Degrees)
data = {
    "H2O": {"TA_pillar": [57.0, 36.0, 32.0], "TA_smooth": [90.0, 90.0]},
    "TEAB": {"TA_pillar": [42.0, 52.0, 47.0, 46.0], "TA_smooth": [74.0]},
    "50pg": {"TA_pillar": [43.0, 90.0], "TA_smooth": [90.0]},
    "200pg": {"TA_pillar": [77.0, 90.0, 74.0], "TA_smooth": [74.0]},
}

# Define Custom Colors
custom_colors = {
    "H2O": "skyblue",
    "TEAB": "#468B97",
    "50pg": "#E6A8D7",
    "200pg": "#F4C2C2",
}

# Convert Tilt Angles from Degrees to Radians & Compute Mean & Standard Deviation
means_radians = {}
std_radians = {}

for reagent, angles in data.items():
    means_radians[reagent] = {
        key: np.radians(np.mean(vals)) for key, vals in angles.items()
    }
    std_radians[reagent] = {
        key: np.radians(np.std(vals, ddof=1)) if len(vals) > 1 else 0 for key, vals in angles.items()
    }

# Create Polar Plot
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'}, figsize=(8, 8))

# Lists to store legend items separately for sorting
pillar_handles = []
pillar_labels = []
smooth_handles = []
smooth_labels = []

for reagent, angles in means_radians.items():
    angle_pillar = angles["TA_pillar"]
    angle_smooth = angles.get("TA_smooth")  # Get TA_smooth if it exists

    # Standard deviation (error) in radians
    error_pillar = std_radians[reagent]["TA_pillar"]

    # Get reagent-specific color
    color = custom_colors.get(reagent, "black")

    # Compute mean angle in degrees
    mean_angle_pillar = np.degrees(angle_pillar)
    mean_angle_smooth = np.degrees(angle_smooth) if angle_smooth is not None else None

    # Plot Main Tilt Angle Line for `TA_pillar`
    line1, = ax.plot([angle_pillar, angle_pillar], [0, 1], linestyle='-', linewidth=2, color=color)

    # Add `TA_pillar` line to the sorted legend list
    pillar_handles.append(line1)
    pillar_labels.append(f"{reagent} - TA_pillar ({mean_angle_pillar:.1f}°)")

    # Plot `TA_smooth` as a Dot Instead of a Line
    if angle_smooth is not None:
        dot = ax.scatter(angle_smooth, 1, color=color, s=80, edgecolors="black", zorder=3)
        smooth_handles.append(dot)
        smooth_labels.append(f"{reagent} - TA_smooth ({mean_angle_smooth:.1f}°)")

    # Plot Shaded Standard Deviation for `TA_pillar`
    if error_pillar > 0:
        ax.fill_betweenx([0, 1], angle_pillar - error_pillar, angle_pillar + error_pillar,
                         alpha=0.2, color=color)

# Adjust Polar Plot Settings
ax.set_theta_zero_location("E")
ax.set_theta_direction(1)

# Set Tick Positions Before Labeling
tick_positions = [0, np.pi / 2, np.pi, 3 * np.pi / 2]
ax.set_xticks(tick_positions)
ax.set_xticklabels(["0°", "90°", "180°" "270°"])

# Remove Radial Labels (Numbers on Rings)
ax.set_yticklabels([])

# Move Title Higher to Avoid Overlap
ax.set_title("Tilt Angle Comparison (Polar Plot) - Shaded Std Dev", y=1.15)

# Combine Sorted Legend Items (TA_pillar first, then TA_smooth)
ax.legend(pillar_handles + smooth_handles, pillar_labels + smooth_labels, loc="upper right", bbox_to_anchor=(1.3, 1))

# Display Plot
plt.show()
