import numpy as np
import matplotlib.pyplot as plt

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

# Choose colors (Change these to modify plot appearance)
color_R = 'blue'  # Change to any color e.g., 'green', 'black'
color_F = 'red'   # Change to any color e.g., 'purple', 'orange'

# Create the plot
plt.figure(figsize=(10, 5))

# Plot R surfaces with error bars
plt.errorbar(surfaces_R, roughness_R, yerr=std_roughness_R,
             fmt='o-', capsize=5, label="Roughness Factor (R)", color=color_R)

# Plot F surfaces with error bars
plt.errorbar(surfaces_F, roughness_F, yerr=std_roughness_F,
             fmt='s--', capsize=5, label="Roughness Factor (F)", color=color_F)

# Labels and title
plt.xlabel("Surface Type")
plt.ylabel("Roughness Factor")
plt.title("Roughness Factors")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
