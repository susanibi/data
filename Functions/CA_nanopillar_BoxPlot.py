import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Hardcoded data
theta_Y_R0 = 149.1  # Young's angle for R surfaces
theta_Y_F0 = 134.5  # Young's angle for F surfaces

theta_W_R = np.array([162.8, 168.5, 169.8, 167.8, 166.2, 166.9, 166.9, 169.9, 165.3])
theta_W_F = np.array([160.6, 162.7, 163.3, 163.6, 166.5, 165.9, 166.1, 165.9, 166.7])

std_R_full = np.array([14.7, 10.9, 4.7, 3.9, 3.7, 2.3, 3.1, 2.9, 4.0, 2.9])
std_F_full = np.array([0.6, 1.1, 1.3, 1.1, 1.2, 1.2, 1.1, 1.2, 1.3, 1.6])

# Define function to calculate roughness factor and uncertainty propagation
def calculate_roughness(theta_W, theta_Y):
    return np.cos(np.radians(theta_W)) / np.cos(np.radians(theta_Y))

def roughness_std(theta_W, theta_Y, std_theta_W):
    return np.abs(np.sin(np.radians(theta_W)) / np.cos(np.radians(theta_Y))) * np.radians(std_theta_W)

# Compute roughness factors
roughness_R = calculate_roughness(theta_W_R, theta_Y_R0)
roughness_F = calculate_roughness(theta_W_F, theta_Y_F0)

# Compute roughness factor standard deviations (properly propagating R_0 and F_0)
std_roughness_R = roughness_std(theta_W_R, theta_Y_R0, std_R_full[1:]) + roughness_std(theta_Y_R0, theta_Y_R0, std_R_full[0])
std_roughness_F = roughness_std(theta_W_F, theta_Y_F0, std_F_full[1:]) + roughness_std(theta_Y_F0, theta_Y_F0, std_F_full[0])

# Labels for surfaces
surfaces_R = [f"R_{i}" for i in range(2, 11)]
surfaces_F = [f"F_{i}" for i in range(2, 11)]

# 🎨 Define ultra-soft color gradients
f_gradient_cmap = mcolors.LinearSegmentedColormap.from_list("f_gradient", ["#ABF2DB", "#3A755E"])
r_gradient_cmap = mcolors.LinearSegmentedColormap.from_list("r_gradient", ["#B3DAFB", "#485E78"])

# Generate gradient colors dynamically
color_R = [r_gradient_cmap(i / (len(surfaces_R) - 1)) for i in range(len(surfaces_R))]
color_F = [f_gradient_cmap(i / (len(surfaces_F) - 1)) for i in range(len(surfaces_F))]

# Create the plot
fig, ax = plt.subplots(figsize=(10, 5))

# Plot F surfaces with gradient colors
for i, surface in enumerate(surfaces_F):
    ax.errorbar(surface, roughness_F[i], yerr=std_roughness_F[i],
                fmt='s', capsize=5, color=color_F[i], label="F (Gradient)" if i == 0 else "")

# Plot R surfaces with gradient colors
for i, surface in enumerate(surfaces_R):
    ax.errorbar(surface, roughness_R[i], yerr=std_roughness_R[i],
                fmt='o', capsize=5, color=color_R[i], label="R (Gradient)" if i == 0 else "")



# Labels and title (Increased font size)
ax.set_xlabel("Surface Type", fontsize=14)
ax.set_ylabel("Roughness Factor", fontsize=14)
ax.set_title("Roughness Factor", fontsize=16)

# Light grey grid
ax.grid(True, linestyle="--", color="lightgrey", linewidth=0.7)

# Move legend outside the plot
ax.legend(loc="upper left", bbox_to_anchor=(1, 1), fontsize=12)

# Rotate x-axis labels
plt.xticks(rotation=45)

# Adjust layout to fit legend
plt.tight_layout()

# Show the plot
plt.show()
