import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Define the Stokes-based exponential model
def stokes_model(t, k, Amax):
    return Amax * (1 - np.exp(-k * t))

# Experimental data
minutes = [1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1, 8.1, 9.1, 10.1, 11.1, 12.1, 13.1, 14.1, 15.1, 16.1, 17.1, 18.1, 19.1, 21.1, 23.1, 25.1, 27.1, 29.1, 31.1, 33.1, 35.1, 37.1, 39.1, 41.1, 43.1, 45.1, 47.1, 49.1, 51.1, 53.1, 55.1, 57.1, 59.1, 61.1, 63.1, 65.2, 67.1, 69.2, 71.2, 73.2, 75.2, 77.2, 79.2, 81.2, 83.2, 85.2, 87.2, 89.2]
pbs_avg = [0.00167328, 0.00283166, 0.003573553, 0.004853695, 0.005830436, 0.007125053, 0.008444693, 0.00973276, 0.011057026, 0.012187284, 0.013835075, 0.015265113, 0.016267248, 0.017316984, 0.018588932, 0.019501295, 0.020457719, 0.021703545, 0.022769702, 0.025308803, 0.027197265, 0.029354043, 0.031429227, 0.033541443, 0.035671539, 0.037555691, 0.039484473, 0.04122776, 0.04327804, 0.044928422, 0.046717339, 0.048162452, 0.050037406, 0.051498855, 0.053162235, 0.054841475, 0.056392893, 0.057939377, 0.059099789, 0.060414123, 0.0619389, 0.063193465, 0.064538681, 0.065627034, 0.06672856, 0.067773119, 0.06879933, 0.069881557, 0.070636206, 0.071700865, 0.072649387, 0.073792878, 0.074658547, 0.075559492]
pbs_std = [0.000516406, 0.000349957, 0.000651878, 0.000561347, 0.001104362, 0.000906071, 0.001284462, 0.001092317, 0.001139782, 0.00145362, 0.001551485, 0.001358802, 0.001144692, 0.002151885, 0.002147317, 0.0024404, 0.002387296, 0.00240244, 0.00266046, 0.002566721, 0.002780998, 0.003103826, 0.003101644, 0.003158957, 0.003424384, 0.003471999, 0.003671039, 0.003654786, 0.00393725, 0.004216321, 0.004363728, 0.004257718, 0.004635243, 0.00476639, 0.004790422, 0.004810246, 0.005080641, 0.005232063, 0.005388489, 0.005361648, 0.005471034, 0.005707399, 0.005873734, 0.005911773, 0.006015363, 0.006188863, 0.006239134, 0.006436274, 0.006543383, 0.006743681, 0.006839209, 0.007018738, 0.007202851, 0.007192122]
f68_avg = [0.000755776, 0.001090931, 0.001809684, 0.002385009, 0.002950734, 0.003524792, 0.004294577, 0.005189985, 0.0058503, 0.00653045, 0.007030729, 0.007745136, 0.008407076, 0.008974355, 0.009762282, 0.01018358, 0.010757739, 0.011134062, 0.011910275, 0.013016738, 0.013866115, 0.015006003, 0.01574757, 0.016852415, 0.017831462, 0.01877656, 0.019781457, 0.020833816, 0.021750618, 0.022466751, 0.023424877, 0.024016561, 0.024823627, 0.025629416, 0.026402839, 0.027321365, 0.028052004, 0.028857495, 0.029766995, 0.030264213, 0.031111699, 0.031586787, 0.031885561, 0.032640139, 0.032889833, 0.033318744, 0.033652435, 0.034002539, 0.034096047, 0.034618886, 0.034945609, 0.035521931, 0.036151954, 0.036676062]
f68_std = [0.000261082, 0.000444121, 0.00030771, 0.000359243, 0.000627301, 0.000600504, 0.00067765, 0.0004285, 0.000535386, 0.001010043, 0.000834982, 0.000929623, 0.000873684, 0.001204247, 0.001532681, 0.001384108, 0.001797753, 0.00166531, 0.001765935, 0.001897393, 0.002463805, 0.00274626, 0.002085869, 0.001983235, 0.002015258, 0.001861966, 0.002185344, 0.002324861, 0.002600033, 0.002395446, 0.002560313, 0.002601807, 0.002811974, 0.003084539, 0.003135038, 0.003338946, 0.003262764, 0.003520716, 0.003700452, 0.003800601, 0.00393814, 0.004213046, 0.004766744, 0.00490367, 0.005068213, 0.005341133, 0.005367249, 0.005787841, 0.005738693, 0.005821637, 0.006006451, 0.00613603, 0.006189173, 0.006277071]

# Convert to arrays
x         = np.array(minutes)
pbs_exp   = np.array(pbs_avg)
pbs_std   = np.array(pbs_std)
f68_exp   = np.array(f68_avg)
f68_std   = np.array(f68_std)

# Fit PBS model
popt, _    = curve_fit(stokes_model, x, pbs_exp, bounds=([0, 0], [1, 1]), p0=[0.03, 0.5])
k_fit, Amax_fit = popt
pbs_model  = stokes_model(x, k_fit, Amax_fit)

# Theoretical F68 models at adjusted k
f68_model_10 = stokes_model(x, k_fit * (0.8, Amax_fit)
f68_model_30 = stokes_model(x, k_fit * (0.45, Amax_fit)

# Ideal curve for secondary axis
k_ideal    = 0.01667
time_ideal = np.linspace(0, x.max(), 300)
ideal_curve = stokes_model(time_ideal, k_ideal, 1.0)

# Define colors (including "ideal")
colors = {
    "pbs_exp":      "#AEC6CF",
    "pbs_model":    "#C89BB7",    # Darker tone
    "f68_exp":      "#748D8E",
    "f68_model":    "#ADD8E6",    # Lighter blue
    "fill_between": "lightgrey",
   # "ideal":        "#C89BB7"
}

# 1) Create figure and primary axis
fig, ax1 = plt.subplots(figsize=(12, 6))

# 2) Plot experimental PBS & F68 data + model fits
ax1.errorbar(x, pbs_exp, yerr=pbs_std, fmt='o-',
             color=colors["pbs_exp"], capsize=3,
             markersize=4, linewidth=1.5, label="PBS")
ax1.errorbar(x, f68_exp, yerr=f68_std, fmt='s-',
             color=colors["f68_exp"], capsize=3,
             markersize=4, linewidth=1.5, label="F68")
ax1.plot(x, pbs_model, '--',
         color=colors["pbs_model"], linewidth=2, label="PBS fit")
ax1.fill_between(x, f68_model_30, f68_model_10,
                 color=colors["fill_between"], alpha=0.2,
                 label="F68 theoretical accumulation")

# 3) Labels, grid, and legend
ax1.set_xlabel("Time (minutes)", fontsize=14)
ax1.set_ylabel("TANorm a.u.", fontsize=14)
ax1.grid(True)

# 4) Secondary axis for ideal reference
#ax2 = ax1.twinx()
#ax2.set_ylabel("Normalized Accumulation (Ideal)", fontsize=12)
#ax2.set_ylim(0, 1.05)
#ax2.plot(time_ideal, ideal_curve, '--',
         #color=colors["ideal"], linewidth=2,
         #label="Ideal Sedimentation (normalized)")
#ax2.tick_params(axis='y', labelcolor='black')

# 5) Combine legends from both axes
lines1, labels1 = ax1.get_legend_handles_labels()
#lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1, labels1, fontsize=14, loc='upper left')
#ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=10, loc='upper left')
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.title("", fontsize=16)
fig.tight_layout()
plt.show()
