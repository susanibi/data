# Repeat with Protein Group data
data = pd.DataFrame({
    "Sample": [
        "B6", "B7", "B8", "A8", "B2", "A2", "A12", "B5",
        "A7", "A3", "A9", "A11", "B3", "B4", "A5",
        "A6", "A1", "A10", "A4", "B1"
    ],
    "%F68": ["0", "0", "0", "0", "0", "0.03", "0.05", "0.05",
             "0", "0.03", "0.03", "0.03", "0.03", "0.03", "0.05",
             "0", "0", "0.03", "0.05", "0.05"],
    "HeLa (pg)": [0, 0, 0, 50, 50, 50, 50, 50,
                  125, 125, 125, 125, 125, 125, 125,
                  200, 200, 200, 200, 200],
    "Protein Groups": [315, 279, 134, 1259, 1149, 1721, 1417, 1461,
                       2011, 2145, 2067, 2003, 2059, 1966, 2071,
                       2167, 2224, 2114, 2144, 1824]
})

evotest_prot = pd.DataFrame({
    "HeLa (pg)": [125, 125, 125],
    "%F68": ["evotest"] * 3,
    "Protein Groups": [2208, 2223, 2044]
})

# Combine and summarize
full_data = pd.concat([data[["HeLa (pg)", "%F68", "Protein Groups"]], evotest_prot])
summary = full_data.groupby(["HeLa (pg)", "%F68"]).agg(
    Avg=("Protein Groups", "mean"),
    SEM=("Protein Groups", sem),
    Replicates=("Protein Groups", "count")
).reset_index()

# Unique HeLa levels
hela_levels = sorted(summary["HeLa (pg)"].unique())
bar_width = 0.18

fig, ax = plt.subplots(figsize=(10, 6))

for i, hela in enumerate(hela_levels):
    subset = summary[summary["HeLa (pg)"] == hela]
    f68s = subset["%F68"].tolist()
    n = len(f68s)
    offsets = np.linspace(-bar_width * n / 2, bar_width * n / 2, n)
    for j, (offset, row) in enumerate(zip(offsets, subset.itertuples())):
        x = i + offset
        ax.bar(x, row.Avg, width=bar_width, yerr=row.SEM, capsize=5,
               color=f'tab:{["blue","green","red","gray"][j]}', label=row._2 if i == 0 else "")
        ax.text(x, row.Avg * 0.05, f"n={row.Replicates}", ha='center', va='bottom', color='white', fontsize=8)

# Axis + legend
ax.set_xticks(range(len(hela_levels)))
ax.set_xticklabels(hela_levels)
ax.set_xlabel("HeLa (pg)")
ax.set_ylabel("Average Protein Groups ± SEM")
ax.set_title("Protein Groups vs. HeLa (pg) grouped by %F68\nDynamic spacing with Evotest at 125 pg")
ax.legend(title="%F68")
ax.grid(axis='y')
plt.tight_layout()
plt.show()
